from fasthtml.common import *

def SortableColumnsJs():
    src = """
        import { Sortable } from 'https://cdn.jsdelivr.net/npm/sortablejs/+esm';

        document.addEventListener('DOMContentLoaded', function() {
            initSortable();
        });

        function initSortable() {
            const headerRow = document.getElementById('column-header-row');

            if (!headerRow) return;

            // Initialize SortableJS on the header row
            new Sortable(headerRow, {
                animation: 150,
                ghostClass: 'sortable-ghost',
                onEnd: function(evt) {
                    // Get the new column order
                    const headers = Array.from(headerRow.children);
                    const columnOrder = headers.map(header => 
                        header.getAttribute('data-col'));

                    // Send the new order to the server using htmx as a POST request
                    htmx.ajax('POST', '/reorder_columns', {
                        target: '#experiment-table',
                        swap: 'innerHTML',
                        values: {
                            order: columnOrder.join(',')
                        }
                    });
                }
            });
        }

        // Re-initialize Sortable after HTMX content swaps
        document.body.addEventListener('htmx:afterSwap', function(evt) {
            if (evt.detail.target.id === 'experiment-table') {
                initSortable();
            }
        });
        """
    return Script(src, type='module')
