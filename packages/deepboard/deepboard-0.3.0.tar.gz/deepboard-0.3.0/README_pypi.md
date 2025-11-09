# Deepboard
This package include two modules that are work together: 
`deepboard gui` and `resultTable`. The `resultTable` module 
keeps track of all of your experiment and helps you organize 
your code to make results reproducible. The `deepboard gui` module
implement a webUI to visualize the training details and training 
curves of any runs. In addition, it lets you commpare training curves
between runs. You can even download the charts that you have generated:)
## 🔥 Screenshots 🔥
![](https://raw.githubusercontent.com/anthol42/deepboard/main/assets/main_view.png)


![](https://raw.githubusercontent.com/anthol42/deepboard/main/assets/compare_view.png)


![](https://raw.githubusercontent.com/anthol42/deepboard/main/assets/full_table_view.png)
## 🌟 Project Philosophy
Before diving in, it’s important to understand the philosophy behind this project. In deep learning, it’s easy to get 
swept up in the excitement — experimenting with countless configurations in search of the perfect setup. 🔬✨ 
Eventually, we stumble upon something that works well... only to keep tweaking and lose track of what actually worked 
best. This package is built to help you stay focused, organized, and efficient — so you never lose track of that perfect 
combination again. 🧠✅

The idea is simple: always make your code reproducible!
Sure, easier said than done... 😅 My recommended approach is to use a multi-level configuration system. Let me explain 
how it works! 👇

Before jumping into experiments, we usually know the minimal set of parameters required for a project to run.
For instance, if you're training a Transformer model, you already know you'll need to specify things like the number of 
layers, number of attention heads, learning rate, and so on. All these known parameters can (and should) be stored in a 
configuration file — I personally prefer using YAML for its readability. 📄 When running the experiment, we simply load 
this config file and use it to parameterize each part of the code. Usually, the parameters stored in the config gives 
us the baseline.

Once we’ve established a baseline, it’s natural to want to improve it — whether it's by testing out a new technique from
a paper or an idea that came to us in a dream. 🚀 But here's the challenge: how do we add new functionality to our code 
without breaking compatibility with earlier runs? In other words, if we use the same config file and script parameters, 
we should still get the exact same results as before. My solution? Add new parameters to functions with sensible 
default values — specifically, defaults that reflect the original behavior. You can then include these parameters in 
your configuration file and toggle them on or off to test their effect. For example, say you’re building an image 
classifier and want to try `MixUp`. Your training function might look like this:
```python
def train_model(..., use_mixup: bool = False):
    ...
```
By setting the default to False, your baseline run remains intact. Only when `use_mixup` is explicitly set to True will 
the new logic kick in. This approach ensures clean, reproducible experimentation with minimal disruption. ✅

Sometimes, we don’t want to modify the configuration file directly — for example, when we've decided that a particular 
config represents a fixed setup for a specific model or training strategy.
In these cases, it's often more convenient to override a few parameters via the command line. 🧪
To do this, I use Python’s built-in argparse module. It adds an extra layer of configuration that’s ideal for quick 
experiments — without changing the original YAML file. And just like before, the same principle applies: always use 
default values that reproduce the results of previous runs. This ensures your experiments stay flexible and reproducible. 🔁

This project promotes a simple but powerful principle: make your deep learning experiments reproducible — without 
slowing down iteration or innovation. To achieve that, it recommends a multi-level configuration system:
1. YAML Configuration Files – Store all known parameters for a clean, reproducible baseline. 📄
2. Function Defaults – Add new features with default values that preserve past behavior. This ensures that re-running 
with the same config and cli parameters always gives the same result. ✅
3. CLI Overrides – For quick tweaks, use cli parameters to add new functionalities or to override config's parameters 
without editing the base config. Perfect for fast experimentation. 🧪

This layered setup keeps your workflow organized, traceable, and easy to extend, so you can explore new ideas without 
losing sight of what actually works. 🔁

If you're feeling a bit overwhelmed or would like a project example, the 
[torchbuilder](https://github.com/anthol42/torchbuilder/tree/dev) app can generate various project templates. The 
default template implements this philosophy, including the resultTable, making it a great starting point! 🚀

## 🛠️ Installation
To install only the `resultTable` module, which allows you to log your results inside a single file, you can run:
```shell
pip install deepboard
```

To also install the `GUI` module, which allows you to visualize your results in a web UI, you can run:
```shell
pip install deepboard[full]
```

## 🚀 How to Use
For your project, you will only need the `resultTable` module, as the `deepboard` module is primarily for the UI.

### ResultTable
First, import the `ResultTable` class from `deepboard.resultTable`, then create a new run. You can also create a debug run. 
A **debug run** will be logged in the result table like any other run, but all results will be overwritten by the next 
debug run. This helps keep the result table clean by containing only the runs you intend to test, rather than those 
meant solely for verifying if the code executed correctly.

Note: **Debug runs always have a runID of -1.** 🔧
```python
from deepboard.resultTable import ResultTable
    
rtable = ResultTable("results/resultTable.db")
if DEBUG:
    resultSocket = rtable.new_debug_run("Experiment1", "path/to/config", cli=vars(args).copy())
else:
    resultSocket = rtable.new_run("Experiment1", "path/to/config", cli=vars(args).copy())
```

Next, you can specify hyperparameters that will appear in the table
```python
resultSocket.add_hparams(
        lr=config["training"]["learning_rate"],
        wd=...,
        min_lr=...,
        dropout2d=...,
        dropout=...
    )
```

During training, we can log scalars associated to the run with:
```python
resultSocket.add_scalar(f'Train/Accuracy', 0.99, step)
```

Finally, you can log the final evaluation results that will be included into the table with:
```python
resultSocket.write_result(accuracy=final_accuracy, crossEntropy=final_loss)
```

Note: If you want to do multiple training iterations of the same run (to test variance for example), you can call the 
```resultSocket.new_repetition``` method after each repetition. 
```python
for rep in range(number_of_repetitions):
    for epoch in range(n_epochs):
        ... # Train here
    resultSocket.new_repetition()

# Finally, write the final results once:
resultSocket.write_result(accuracy=accuracies.mean(), crossEntropy=losses.mean())
```

### Deepboard UI
To launch deepboard Web UI, simply run the command `deepboard` in your terminal with the path to your resultTable db:
```shell
deepboard /path/to/resultTable.db
```