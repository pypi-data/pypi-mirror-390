from traceback import print_tb
from typing import *
from .cursor import Cursor
from datetime import datetime
from .scalar import Scalar
import sys
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
import hashlib

class LogWriter:
    """
    This class makes an object that is bound to a run row in the result table. This means that everything that is
    logged through this object is added into the result table and this object can be used to interact with a specific
    run. This object is single use. This means that once the final results are written, the object becomes read-only.

    You should not instantiate this class directly, but use the ResultTable class to create it instead.

    """
    def __init__(self, db_path, run_id: int, start: datetime, flush_each: int = 10, keep_each: int = 1,
                 disable: bool = False, auto_log_plt=True):
        """
        :param db_path: The path to the database file
        :param run_id: The run id of this run
        :param start: The start time of this run
        :param flush_each: Every how many logs should we write them to the database. (increase it to reduce io)
        :param keep_each: Every how many logs datapoint should we store. The others will be discarted. If 2, only one
        datapoint every two times the add_scalar method is called will be stored.
        :param disable: If True, the logger is disabled and will not log anything in the database.
        :param auto_log_plt: If True, automatically detect if matplotlib figures were generated and log them. Note that
        it checks only when a method on the LogWriter is called.
        """
        if keep_each <= 0:
            raise ValueError("Parameter keep_each must be grater than 0: {1, 2, 3, ...}")
        if flush_each <= 0:
            raise ValueError("Parameter keep_each must be grater than 0: {1, 2, 3, ...}")
        self.db_path = db_path
        self.run_id = run_id
        self.start = start
        self.flush_each = flush_each
        self.keep_each = keep_each


        self.global_step = {}
        self.buffer = {}
        self.log_count = {}

        self.image_buffer = []
        self._processed_figs = set()

        self.fragments_buffer = []

        self.enabled = True
        self.run_rep = 0
        self.disable = disable

        self.pre_hooks: List[Callable[[], None]] = []

        if auto_log_plt:
            self.pre_hooks.append(self.detect_and_log_figures)

        # Set the exception handler to set the status to failed and disable the logger if the program crashes
        self._exception_handler()

    def new_repetition(self):
        """
        Create a new repetition of the current run. This is useful if you want to log multiple repetitions of the same
        run. This is a mutating method, meaning that you can call it at the end of the training loop before the next
        full training loop is run again.
        :return: None
        """
        # Start by flushing the buffer
        for tag in self.buffer.keys():
            self._flush(tag)

        self.run_rep += 1

        # Reset the writer
        self.log_count = {}
        self.global_step = {}
        self.start = datetime.now()

    def add_scalar(self, tag: str, scalar_value: Union[float, int],
                   step: Optional[int] = None, epoch: Optional[int] = None,
                   walltime: Optional[float] = None, flush: bool = False):
        """
        Add a scalar to the resultTable
        :param tag: The tag, formatted as: 'split/name' or simply 'split'
        :param scalar_value: The value
        :param step: The global step. If none, the one calculated is used
        :param epoch: The epoch. If None, none is saved
        :param walltime: Override the wall time with this
        :param flush: Force flush all the scalars in memory
        :return: None
        """
        self._run_pre_hooks()
        if not self.enabled:
            raise RuntimeError("The LogWriter is read only! This might be due to the fact that you loaded an already"
                               "existing one or you reported final metrics.")
        # Early return if we are not supposed to keep this run.
        if not self._keep(tag):
            return

        # We split the tag as a split and a name for readability
        splitted_tag = tag.split("/")
        if len(splitted_tag) == 2:
            split, name = splitted_tag[0], splitted_tag[1]
        else:
            split, name = "", splitted_tag[0]

        scalar_value = float(scalar_value)  # Cast it as float

        step = self._get_global_step(tag) if step is None else step

        walltime = (datetime.now() - self.start).total_seconds() if walltime is None else walltime

        epoch = 0 if epoch is None else epoch

        # Added a row to table logs
        self._log(tag, epoch, step, split, name, scalar_value, walltime, self.run_rep)

        # Flush all if requested to force flush
        if flush:
            self._flush_all()

    def get_scalar(self, tag) -> List[Scalar]:
        """
        Read a scalar from the resultTable with the given tag
        :param tag: The tag to read formatted as: 'split/name' or simply 'split'.
        :return: A list of Scalars items
        """
        splitted_tag = tag.split("/")
        if len(splitted_tag) == 2:
            split, name = splitted_tag[0], splitted_tag[1]
        else:
            split, name = "", splitted_tag[0]

        with self. _cursor as cursor:
            cursor.execute("SELECT * FROM Logs WHERE run_id=? AND split=? AND label=?", (self.run_id, split, name))
            # cursor.execute("SELECT * FROM Logs", (self.run_id, split, name))
            rows = cursor.fetchall()
            return [Scalar(*row[1:]) for row in rows]

    def add_image(self, image: Union[bytes, Image.Image], step: Optional[int] = None, tag: Optional[str] = None,
                  epoch: Optional[int] = None, flush: bool = False):
        """
        Add an image to the resultTable
        :param image: Must be png bytes or a PIL Image object.
        :param step: The global step at which the image was generated. If None, the maximum step is taken from all global
        steps.
        :param tag: A tag describing the image.
        :param epoch: The epoch at which the image was generated. If None, no epoch is saved.
        :param flush: If True, flush all data in memory to the database.
        :return: None
        """
        self._run_pre_hooks()
        if isinstance(image, Image.Image):
            buffer = BytesIO()
            image.save(buffer, format='PNG')
            img_bytes = buffer.getvalue()
        else:
            img_bytes = image

        if step is None:
            # Take the max step from scalars
            step = max(self.global_step.values()) if self.global_step else 0

        # Add to buffer
        self._log_image(img_bytes, step, tag, self.run_rep, epoch)

        if flush:
            self._flush_all()

    def get_images(self, id: Optional[int] = None, step: Optional[int] = None, tag: Optional[str] = None, epoch: Optional[int] = None,
                    repetition: Optional[int] = None) -> List[dict]:
        """
        Return all images logged in the run with the given step, tag and/or epoch.
        :param id: The id of the image to read
        :param step: The step at which the image was generated. If None, all images are returned.
        :param tag: The tag in which the images were generated. If None, all tags are returned.
        :param epoch: The epoch at which the images were generated. If None, all epochs are returned.
        :param repetition: The repetition of the images. If None, all images are returned.
        :return: A list of image bytes
        """
        return self._get_images(id, step, tag, epoch, repetition, img_type="IMAGE")


    def detect_and_log_figures(self, step: Optional[int] = None, tag: Optional[str] = None,
                               epoch: Optional[int] = None, flush: bool = False, close_figs: bool = False):
        """
        Detect matplotlib figures that are currently open and log them to the result table. (Save them as png).
        :param step: The global step at which the image was generated. If None, the maximum step is taken from all global
        steps.
        :param tag: A tag describing the figures.
        :param epoch: The epoch at which the images were generated. If None, no epoch is saved.
        :param flush: If True, flush all data in memory to the database.
        :param close_figs: If True, close all figures after detection.
        :return: None
        """
        if step is None:
            # Take the max step from scalars
            step = max(self.global_step.values()) if self.global_step else 0

        for num in plt.get_fignums():
            fig = plt.figure(num)
            if fig in self._processed_figs:
                continue
            self._processed_figs.add(fig)
            fig.tight_layout()

            # Save it as bytes
            buffer = BytesIO()
            fig.savefig(buffer, format='png')
            if close_figs:
                plt.close(fig)
            img_bytes = buffer.getvalue()

            self._log_image(img_bytes, step, tag, self.run_rep, epoch, type="PLOT")

        if flush:
            self._flush_all()

    def get_figures(self, id: Optional[int] = None, step: Optional[int] = None, tag: Optional[str] = None, epoch: Optional[int] = None,
                    repetition: Optional[int] = None):
        """
        Return all figures logged in the run with the given step, tag and/or epoch.
        :param id: The id of the figure to read. If None, all figures are returned.
        :param step: The step at which the figure was generated. If None, all figures are returned.
        :param tag: The tag describing the figures. If None, all tags are returned.
        :param epoch: The epoch at which the figures were generated. If None, all epochs are returned.
        :param repetition: The repetition of the figures. If None, all figures are returned.
        :return:
        """
        return self._get_images(id, step, tag, epoch, repetition, img_type="PLOT")

    def add_text(self, text: str, step: Optional[int] = None, tag: Optional[str] = None,
                  epoch: Optional[int] = None, flush: bool = False):
        """
        Add a text sample to the resultTable
        :param text: Must be a string
        :param step: The global step at which the image was generated. If None, the maximum step is taken from all global
        scalar steps.
        :param tag: A tag describing the text.
        :param epoch: The epoch at which the image was generated. If None, no epoch is saved.
        :param flush: If True, flush all data in memory to the database.
        :return: None
        """
        self._run_pre_hooks()
        if step is None:
            # Take the max step from scalars
            step = max(self.global_step.values()) if self.global_step else 0

        self._log_fragment(text, step, tag, self.run_rep, epoch, type="RAW")
        if flush:
            self._flush_all()

    def get_text(self, id: Optional[int] = None, step: Optional[int] = None, tag: Optional[str] = None,
                  epoch: Optional[int] = None, repetition: Optional[int] = None):
        """
        Return all text samples logged in the run with the given id, step, tag and/or epoch.
        :param id: The id of the text sample to read
        :param step: The step at which the text was generated. If None, all text samples are returned.
        :param tag: The tag describing the text. If None, all tags are returned.
        :param epoch: The epoch at which the texts were generated. If None, all epochs are returned.
        :param repetition: The repetition of the run. If None, all text samples are returned.
        :return: A list of text samples
        """
        return self._get_fragments(id, step, tag, epoch, repetition, fragment_type="RAW")

    def add_fragment(self, content: str, step: Optional[int] = None, tag: Optional[str] = None,
                  epoch: Optional[int] = None, flush: bool = False):
        """
        Add a html fragment to the resultTable
        :param content: Must be a string containing valid HTML content.
        :param step: The global step at which the image was generated. If None, the maximum step is taken from all global
        scalar steps.
        :param tag: A tag describing the fragment.
        :param epoch: The epoch at which the image was generated. If None, no epoch is saved.
        :param flush: If True, flush all data in memory to the database.
        :return: None
        """
        self._run_pre_hooks()
        if step is None:
            # Take the max step from scalars
            step = max(self.global_step.values()) if self.global_step else 0

        self._log_fragment(content, step, tag, self.run_rep, epoch, type="HTML")
        if flush:
            self._flush_all()

    def get_fragment(self, id: Optional[int] = None, step: Optional[int] = None, tag: Optional[str] = None,
                  epoch: Optional[int] = None, repetition: Optional[int] = None):
        """
        Return all html fragments logged in the run with the given id, step, tag and/or epoch.
        :param id: The id of the html fragment to read
        :param step: The step at which the html fragment was generated. If None, all html fragment are returned.
        :param tag: The tag describing the fragment. If None, all tags are returned.
        :param epoch: The epoch at which the html fragments were generated. If None, all epochs are returned.
        :param repetition: The repetition of the run. If None, all html fragment are returned.
        :return: A list of html fragment
        """
        return self._get_fragments(id, step, tag, epoch, repetition, fragment_type="HTML")

    def add_hparams(self, param_dict: Optional[dict[str, Any]] = None, **kwargs):
        """
        Add hyperparameters to the result table
        :param param_dict: The hyperparameters to add as a dict.
        :param kwargs: The hyperparameters to save
        :return: None
        """
        self._run_pre_hooks()
        # Prepare the data to save
        if self.disable:
            return
        if param_dict is not None:
            kwargs.update(param_dict)

        query = "INSERT INTO Results (run_id, metric, value, is_hparam) VALUES (?, ?, ?, ?)"
        data = [(self.run_id, key, value, True) for key, value in kwargs.items()]
        with self._cursor as cursor:
            cursor.executemany(query, data)

    def get_hparams(self) -> Dict[str, Any]:
        """
        Get the hyperparameters of the current run
        :return: A dict of hyperparameters
        """
        with self._cursor as cursor:
            cursor.execute("SELECT metric, value FROM Results WHERE run_id=? AND is_hparam=1", (self.run_id,))
            rows = cursor.fetchall()
            return {row[0]: row[1] for row in rows}

    def get_repetitions(self) -> List[int]:
        """
        Get the all the repetitions ids of the current run
        :return: A list of repetitions ids
        """
        with self._cursor as cursor:
            cursor.execute("SELECT DISTINCT run_rep FROM Logs WHERE run_id=?", (self.run_id,))
            rows = cursor.fetchall()
            return [row[0] for row in rows]

    def write_result(self, **kwargs):
        """
        Log the results of the run to the table, then disable the logger. This means that the logger will be read-only
        after this operation. If you run multiple iterations, consider writing the results only once all the runs are
        finished. You can aggregate the different metrics before passing them.
        :param kwargs: The metrics to save
        :return: None
        """
        self._run_pre_hooks()
        if self.disable:
            return
        # Start by flushing the buffer
        self._flush_all()

        # Then, prepare the data to save
        query = "INSERT INTO Results (run_id, metric, value, is_hparam) VALUES (?, ?, ?, ?)"
        data = [(self.run_id, key, value, False) for key, value in kwargs.items()]
        with self._cursor as cursor:
            cursor.executemany(query, data)

        # Set the status to finished
        self.set_status("finished")

        # Disable the logger
        self.enabled = False

    def set_status(self, status: Literal["running", "finished", "failed"]):
        """
        Manually set the status of the run
        :param status: The status to set
        :return: None
        """
        self._run_pre_hooks()
        if self.disable:
            return
        if status not in ["running", "finished", "failed"]:
            raise ValueError("Status must be one of: running, finished, failed")
        with self._cursor as cursor:
            cursor.execute("UPDATE Experiments SET status=? WHERE run_id=?", (status, self.run_id))

    def set_note(self, note: str):
        """
        Update the note of the run
        :param note: The note to set (will overwrite the previous one)
        :return: None
        """
        self._run_pre_hooks()
        if self.disable:
            return
        with self._cursor as cursor:
            cursor.execute("UPDATE Experiments SET note=? WHERE run_id=?", (note, self.run_id))

    def set_tag(self, tag: str):
        """
        Update the tag of the run
        :param tag: The tag to set (will overwrite the previous one)
        :return: None
        """
        self._run_pre_hooks()
        if self.disable:
            return
        with self._cursor as cursor:
            cursor.execute("UPDATE Experiments SET tag=? WHERE run_id=?", (tag, self.run_id))

    def set_color(self, color: Optional[str] = None):
        """
        Set the color of the run
        :param color: The color to set (hex format without #, e.g. 'ff0000' for red)
        :return: None
        """
        self._run_pre_hooks()
        if self.disable:
            return

        if color is not None and 6 < len(color) > 7:
            raise ValueError(f"Invalid color format, only accept RGB HEX. Got: '{color}'")

        if color is not None and color.startswith('#'):
            color = color[1:]

        with self._cursor as cursor:
            cursor.execute("UPDATE Experiments SET color=? WHERE run_id=?", (color, self.run_id))

    @property
    def tag(self) -> str:
        """
        Get the tag of the run
        :return: The tag of the run
        """
        with self._cursor as cursor:
            cursor.execute("SELECT tag FROM Experiments WHERE run_id=?", (self.run_id,))
            row = cursor.fetchone()
        if row is None:
            raise RuntimeError(f"Run {self.run_id} does not exist.")

        return row[0] or "" # If None, return empty string

    @property
    def color(self) -> Optional[str]:
        """
        Get the color of the run
        :return: The color of the run
        """
        with self._cursor as cursor:
            cursor.execute("SELECT color FROM Experiments WHERE run_id=?", (self.run_id,))
            row = cursor.fetchone()
        if row is None:
            raise RuntimeError(f"Run {self.run_id} does not exist.")

        return row[0]

    @property
    def status(self) -> str:
        """
        Get the status of the run
        :return: The status of the run
        """
        with self._cursor as cursor:
            cursor.execute("SELECT status FROM Experiments WHERE run_id=?", (self.run_id,))
            row = cursor.fetchone()
            if row is None:
                raise RuntimeError(f"Run {self.run_id} does not exist.")
            return row[0]

    @property
    def scalars(self) -> List[str]:
        """
        Return the tags of all scalars logged in the run
        """
        # We need to format the tags as Split/Label
        # If split is empty, we just return the label
        rows = [(row[0] + "/" + row[1]) if row[0] != "" else row[1] for row in self.formatted_scalars]
        return rows

    @property
    def formatted_scalars(self) -> List[Tuple[str, str]]:
        """
        Return the scalars values as split and label
        """
        with self._cursor as cursor:
            cursor.execute("SELECT DISTINCT split, label FROM Logs WHERE run_id=?", (self.run_id,))
            rows = cursor.fetchall()
            # We need to format the tags as Split/Label
            # If split is empty, we just return the label
            return [(row[0], row[1]) for row in rows]

    def __getitem__(self, tag):
        """
        Get the scalar values for a given tag.
        """
        return self.get_scalar(tag)

    def _run_pre_hooks(self):
        for hook in self.pre_hooks:
            hook()

    def _get_fragments(self, id: Optional[int], step: Optional[int], tag: Optional[str], epoch: Optional[int],
                    repetition: Optional[int], fragment_type: Literal["RAW", "HTML"]) -> List[dict]:
        command = f"SELECT id_, step, epoch, run_rep, tag, fragment FROM Fragments WHERE run_id=? AND fragment_type='{fragment_type}'"
        params = [self.run_id]
        if id is not None:
            command += " AND id_=?"
            params.append(id)

        if step is not None:
            command += " AND step=?"
            params.append(step)

        if tag is not None:
            command += " AND tag=?"
            params.append(tag)

        if epoch is not None:
            command += " AND epoch=?"
            params.append(epoch)

        if repetition is not None:
            command += " AND run_rep=?"
            params.append(repetition)

        with self._cursor as cursor:
            cursor.execute(f'{command};', tuple(params))
            rows = cursor.fetchall()
            # Convert the bytes to PIL Image objects
            return [dict(
                id=row[0],
                step=row[1],
                epoch=row[2],
                run_rep=row[3],
                tag=row[4],
                fragment=row[5]
            ) for row in rows]

    def _get_images(self, id: Optional[int], step: Optional[int], tag: Optional[str], epoch: Optional[int],
                    repetition: Optional[int], img_type: Literal["IMAGE", "PLOT"]) -> List[dict]:
        command = f"SELECT id_, step, epoch, run_rep, tag, image FROM Images WHERE run_id=? AND img_type='{img_type}'"
        params = [self.run_id]
        if id is not None:
            command += " AND id_=?"
            params.append(id)

        if step is not None:
            command += " AND step=?"
            params.append(step)

        if tag is not None:
            command += " AND tag=?"
            params.append(tag)

        if epoch is not None:
            command += " AND epoch=?"
            params.append(epoch)

        if repetition is not None:
            command += " AND run_rep=?"
            params.append(repetition)

        with self._cursor as cursor:
            cursor.execute(f'{command};', tuple(params))
            rows = cursor.fetchall()
            # Convert the bytes to PIL Image objects
            return [dict(
                id=row[0],
                step=row[1],
                epoch=row[2],
                run_rep=row[3],
                tag=row[4],
                image=Image.open(BytesIO(row[5]))
            ) for row in rows]

    def _get_global_step(self, tag):
        """
        Keep track of the global step for each tag.
        :param tag: The tag to get the step
        :return: The current global step
        """
        if tag not in self.global_step:
            self.global_step[tag] = 0

        out = self.global_step[tag]
        self.global_step[tag] += 1
        return out

    def _log(self, tag: str, epoch: int, step: int, split: str, name: str, scalar_value: float, walltime: float,
             run_rep: int):
        """
        Store the scalar log into the buffer, and flush the buffer if it is full.
        :param tag: The tag
        :param epoch: The epoch
        :param step: The step
        :param split: The split
        :param name: The name
        :param scalar_value: The value
        :param walltime: The wall time
        :param run_rep: The run repetition
        :return: None
        """
        if tag not in self.buffer:
            self.buffer[tag] = []
        self.buffer[tag].append((self.run_id, epoch, step, split, name, scalar_value, walltime, run_rep))

        if len(self.buffer[tag]) >= self.flush_each:
            self._flush(tag)

    def _log_fragment(self, fragment: str, step: int, tag: Optional[int], repetition: int, epoch: Optional[int],
                   type: Literal["RAW", "HTML"] = "RAW"):
        """
        Log a text or html fragment to the resultTable.
        :param fragment: The content to log
        :param step: The step
        :param tag: A tag describing the fragment
        :param repetition: The run repetition
        :param epoch: The epoch
        :param type: Raw (for text only) or HTML (for html content)
        :return: None
        """

        self.fragments_buffer.append((self.run_id, step, epoch, repetition, type, tag, fragment))

        if len(self.fragments_buffer) >= self.flush_each:
            self._flush_fragments()

    def _log_image(self, image: bytes, step: int, tag: Optional[int], repetition: int, epoch: Optional[int],
                   type: Literal["IMAGE", "PLOT"] = "IMAGE"):
        """
        Store the image log into the buffer, and flush the buffer if it is full.
        :param image: The image bytes
        :param step: The step
        :param tag: A tag describing the image
        :param repetition: The run repetition
        :param epoch: The epoch
        :param type: The type of the image, either "IMAGE" or "PLOT". Default is "IMAGE".
        :return: None
        """

        self.image_buffer.append((self.run_id, step, epoch, repetition, type, tag, image))

        if len(self.image_buffer) >= self.flush_each:
            self._flush_images()

    def _flush_all(self):
        """
        Flush all buffers.
        :return: None
        """
        # Flush all the scalars
        for tag in self.buffer.keys():
            self._flush(tag)

        # Flush all the images
        self._flush_images()

        # Flush all the fragments
        self._flush_fragments()

    def _flush_images(self):
        query = """
                INSERT INTO Images (run_id, step, epoch, run_rep, img_type, tag, image)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """
        if not self.disable:
            with self._cursor as cursor:
                cursor.executemany(query, self.image_buffer)

        # Reset the buffer
        self.image_buffer = []

    def _flush_fragments(self):
        query = """
                INSERT INTO Fragments (run_id, step, epoch, run_rep, fragment_type, tag, fragment)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """
        if not self.disable:
            with self._cursor as cursor:
                cursor.executemany(query, self.fragments_buffer)

        # Reset the buffer
        self.fragments_buffer = []

    def _flush(self, tag: str):
        """
        Flush the scalar values into the db and reset the buffer.
        :param tag: The tag to flush
        :return: None
        """
        query = """
                INSERT INTO Logs (run_id, epoch, step, split, label, value, wall_time, run_rep)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """

        if not self.disable:
            with self._cursor as cursor:
                cursor.executemany(query, self.buffer[tag])

        # Reset the buffer
        self.buffer[tag] = []

    def _keep(self, tag: str) -> bool:
        """
        Assert if we need to record this log or drop it. Depends on the kep_each attribute
        :param tag: The tag
        :return: True if we need to keep it and False if we drop it
        """
        if tag not in self.log_count:
            self.log_count[tag] = 0
        self.log_count[tag] += 1
        if self.log_count[tag] >= self.keep_each:
            self.log_count[tag] = 0
            return True
        else:
            return False

    def _exception_handler(self):
        """
        Set the exception handler to set the status to failed and disable the logger if the program crashes
        """
        previous_hooks = sys.excepthook
        def handler(exc_type, exc_value, traceback):
            # Set the status to failed
            self.set_status("failed")
            # Disable the logger
            self.enabled = False

            # Call the previous exception handler
            previous_hooks(exc_type, exc_value, traceback)

        # Set the new exception handler
        sys.excepthook = handler

    @property
    def _cursor(self):
        return Cursor(self.db_path)