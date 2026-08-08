from ..grammar.grammar import Grammar
from ..parser.parser_builder import ParserBuilder
from ..parser.lalr_parser import LALRItem,LALRState
from ..parser.lr0_parser import LR0Item

template = """
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.4/css/jquery.dataTables.css">
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.4/js/jquery.dataTables.js"></script>
</head>
<body>
    <div class="container">
        <h1>
            🔍 Lookaheads Propagation (LALR(1))
        </h1>

        <div class="stats">
            <span>📊 <strong>Edges:</strong> EDGES-COUNT-PLACEHOLDER </span>
        </div>

        <div class="table-wrapper">
            <table id="propagationTable" class="display" style="width:100%;">
                <thead>
                    <tr>
                        <th style="min-width: 80px;">Origin</th>
                        <th style="min-width: 200px;">Source Item</th>
                        <th style="min-width: 70px;">Symbol</th>
                        <th style="min-width: 80px;">Destination</th>
                        <th style="min-width: 200px;">Destination Item</th>
                        <th style="min-width: 200px;">Propagated Lookaheads</th>
                        <th style="min-width: 200px;">Lookaheads</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- CONTENT-PLACEHOLDER -->
                </tbody>
            </table>
        </div>
        <div>
            <details>
                <summary class="state-summary">
                    <h1><span>States details</span><h1>
                </summary>
                <!-- STATES-DETAILS-PLACEHOLDER -->
            </details>
        </div>
    </div>

    <!-- DataTables JS -->
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            padding: 20px;
            margin: 0;
        }

        .container {
            max-width: 100%;
            margin: 0 auto;
            background: #1e293b;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        }

        h1 {
            font-size: 1.8rem;
            font-weight: 600;
            margin: 0 0 8px 0;
            color: #f8fafc;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .subtitle {
            color: #94a3b8;
            font-size: 0.9rem;
            font-weight: 400;
            margin-left: 12px;
        }

        .stats {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            margin-bottom: 20px;
            padding: 12px 16px;
            background: #0f172a;
            border-radius: 8px;
            font-size: 0.9rem;
        }
        .stats span {
            color: #94a3b8;
        }
        .stats strong {
            color: #f8fafc;
            font-weight: 600;
        }

        .dataTables_wrapper {
            font-family: inherit;
        }

        table.dataTable {
            border-collapse: collapse;
            width: 100%;
            background: #1e293b;
            border-radius: 8px;
            overflow: hidden;
        }

        table.dataTable thead th {
            background: #0f172a !important;
            color: #94a3b8 !important;
            font-weight: 600;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            padding: 14px 12px !important;
            border-bottom: 2px solid #334155 !important;
            white-space: nowrap;
            position: sticky;
            top: 0;
            z-index: 10;
        }

        table.dataTable tbody td {
            padding: 10px 12px !important;
            border-bottom: 1px solid #2d3748 !important;
            color: #e2e8f0;
            font-size: 0.85rem;
            vertical-align: middle;
        }

        table.dataTable tbody tr:nth-child(even) {
            background: #1a2538;
        }
        table.dataTable tbody tr:nth-child(odd) {
            background: #1e293b;
        }

        /* Hover */
        table.dataTable tbody tr:hover {
            background: #2d3a52 !important;
            cursor: default;
        }

        .badge-state {
            display: inline-block;
            background: #3b82f6;
            color: white;
            font-weight: 700;
            font-size: 0.75rem;
            padding: 2px 10px;
            border-radius: 9999px;
            font-family: 'JetBrains Mono', 'Cascadia Code', monospace;
            letter-spacing: 0.3px;
            min-width: 36px;
            text-align: center;
        }

        .badge-state.conflict {
            background: #ef4444;
            animation: pulse-border 1.5s infinite;
        }

        .badge-symbol {
            display: inline-block;
            background: #334155;
            color: #e2e8f0;
            font-weight: 600;
            font-size: 0.8rem;
            padding: 2px 10px;
            border-radius: 4px;
            font-family: 'JetBrains Mono', monospace;
            border: 1px solid #475569;
        }

        .item-code {
            font-family: 'JetBrains Mono', 'Cascadia Code', monospace;
            font-size: 0.8rem;
            background: #0f172a;
            padding: 2px 8px;
            border-radius: 4px;
            color: #a5b4fc;
            white-space: nowrap;
            display: inline-block;
            max-width: 300px;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .lookahead-set {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            color: #fbbf24;
            background: #0f172a;
            padding: 2px 8px;
            border-radius: 4px;
            display: inline-block;
        }

        tr.conflict-row {
            border-left: 4px solid #ef4444 !important;
            background: #2d1a1a !important;
        }
        tr.conflict-row td:first-child {
            border-left: 4px solid #ef4444;
            padding-left: 8px !important;
        }
        tr.conflict-row:hover {
            background: #3d2222 !important;
        }

        .conflict-icon {
            color: #ef4444;
            font-weight: bold;
            margin-left: 6px;
            cursor: help;
        }

        @keyframes pulse-border {
            0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
            70% { box-shadow: 0 0 0 6px rgba(239, 68, 68, 0); }
            100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
        }

        .dataTables_filter input {
            background: #0f172a !important;
            border: 1px solid #334155 !important;
            border-radius: 6px !important;
            color: #f8fafc !important;
            padding: 6px 12px !important;
            margin-left: 8px !important;
            width: 220px !important;
        }
        .dataTables_filter input:focus {
            border-color: #3b82f6 !important;
            outline: none !important;
        }
        .dataTables_length select {
            background: #0f172a !important;
            border: 1px solid #334155 !important;
            border-radius: 6px !important;
            color: #f8fafc !important;
            padding: 4px 8px !important;
        }
        .dataTables_info, .dataTables_paginate {
            color: #94a3b8 !important;
            margin-top: 12px !important;
        }
        .paginate_button {
            background: #0f172a !important;
            border: 1px solid #334155 !important;
            color: #e2e8f0 !important;
            border-radius: 4px !important;
            padding: 4px 12px !important;
            margin: 0 2px !important;
        }
        .paginate_button.current {
            background: #3b82f6 !important;
            border-color: #3b82f6 !important;
            color: white !important;
        }

        .table-wrapper {
            overflow-x: auto;
            padding-bottom: 10px;
        }

        .states-section {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #334155;
        }

        .state-detail {
            background: #1a2538;
            border: 1px solid #334155;
            border-radius: 8px;
            margin-bottom: 8px;
            padding: 0;
            transition: border-color 0.2s;
        }

        .state-detail[open] {
            border-color: #3b82f6;
        }

        .state-summary {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 16px;
            cursor: pointer;
            font-weight: 500;
            user-select: none;
            background: #0f172a;
            border-radius: 8px;
        }
        .state-summary:hover {
            background: #1a2538;
        }

        .state-id {
            font-family: 'JetBrains Mono', monospace;
            font-weight: 700;
            color: #60a5fa;
            font-size: 1rem;
            min-width: 48px;
        }

        .state-badge {
            background: #334155;
            color: #94a3b8;
            font-size: 0.75rem;
            padding: 2px 10px;
            border-radius: 9999px;
        }

        .state-content {
            padding: 12px 20px 16px 20px;
            display: flex;
            flex-wrap: wrap;
            gap: 24px;
        }

        .item-group, .transitions {
            flex: 1 1 300px;
            min-width: 250px;
        }

        .item-group h4, .transitions h4 {
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #94a3b8;
            margin: 0 0 8px 0;
            border-bottom: 1px solid #2d3748;
            padding-bottom: 4px;
        }

        .item-group ul, .transitions ul {
            list-style: none;
            padding: 0;
            margin: 0;
        }

        .item-group li {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            padding: 2px 0;
            color: #e2e8f0;
            display: flex;
            flex-wrap: wrap;
            align-items: baseline;
            gap: 6px;
        }

        .lookahead {
            color: #fbbf24;
            font-size: 0.75rem;
            background: #0f172a;
            padding: 0 6px;
            border-radius: 4px;
        }
    </style>
    <script>
    $(document).ready(function() {
        $('#propagationTable').DataTable({
            "pageLength": 25,
            "order": [[0, "asc"]],
            "columnDefs": [
                { "orderable": false, "targets": [1, 4] }
            ],
            "language": {
                "search": "🔎 Filter:",
                "lengthMenu": "Show _MENU_ edges",
                "info": "Showing _START_ to _END_ of _TOTAL_ edges",
                "infoEmpty": "no edges",
                "infoFiltered": "(filtered de _MAX_ total)"
            }
        });
    });
    </script>
</body>
</html>
"""

row_template = """
                    <tr>
                        <td><span class="badge-state">SOURCE-STATE-PLACEHOLDER</span></td>
                        <td><code class="item-code">SOURCE-ITEM-PLACEHOLDER</code></td>
                        <td><span class="badge-symbol">SYMBOL-PLACEHOLDER</span></td>
                        <td><span class="badge-state">DEST-STATE-PLACEHOLDER</span></td>
                        <td><code class="item-code">DEST-ITEM-PLACEHOLDER</code></td>
                        <td><span class="lookahead-set">LOOKAHEADS-PLACEHOLDER</span></td>
                        <td><span class="lookahead-set">TOTAL-LOOKAHEADS-PLACEHOLDER</span></td>
                    </tr>
"""

state_details_template = """
                <details class="state-detail">
                    <summary class="state-summary">
                        <span class="state-id">STATE-INDEX-PLACEHOLDER</span>
                        <span class="state-badge">STATE-ITEMS-PLACEHOLDER</span>
                    </summary>
                    <div class="state-content">
                        <div class="item-group">
                            <h4>Kernel Items</h4>
                            <ul>
STATE-KERNEL-ITEMS-PLACEHOLDER
                            </ul>
                        </div>
                        <div class="item-group">
                            <h4>Non‑kernel Items (Closure)</h4>
                            <ul>
STATE-NON-KERNEL-ITEMS-PLACEHOLDER
                            </ul>
                        </div>
                    </div>
                </details>
"""

def build_propagation_edges_table(g:Grammar) -> str:

    edges,lr0_states = ParserBuilder.build_lookaheads_propagation_edges(g)
    states_dict = { hash(state):state for state in lr0_states }
    lookaheads = ParserBuilder.get_propagated_lookaheads(g)

    rows = []
    edges_count = 0

    for source_state in edges.keys():
        for (source_item,symbol),(dest_state,dest_item) in edges[source_state].items():
            edges_count += 1
            d_state = states_dict[hash(dest_state)]
            row = row_template.replace('SOURCE-STATE-PLACEHOLDER',f'I{source_state.index}')
            row = row.replace('SOURCE-ITEM-PLACEHOLDER',str(source_item))
            row = row.replace('SYMBOL-PLACEHOLDER',symbol.symbol)
            row = row.replace('DEST-STATE-PLACEHOLDER',f'I{d_state.index}')
            row = row.replace('DEST-ITEM-PLACEHOLDER',str(dest_item))
            _lookaheads = lookaheads[(dest_state,dest_item)]
            row = row.replace('TOTAL-LOOKAHEADS-PLACEHOLDER',str(_lookaheads))
            source_lookaheads = lookaheads.get((source_state,source_item),set())
            row = row.replace('LOOKAHEADS-PLACEHOLDER',str(source_lookaheads) if len(source_lookaheads) > 0 else '∅')
            rows.append(row)

    html = template.replace('<!-- CONTENT-PLACEHOLDER -->','\n'.join(rows))
    html = html.replace('EDGES-COUNT-PLACEHOLDER',str(edges_count))

    states_details = []

    for state in sorted(lr0_states,key=lambda state:state.index):
        state_detail_html = state_details_template.replace('STATE-INDEX-PLACEHOLDER',f'I{state.index}')
        items_length = len(state.items)
        state_detail_html = state_detail_html.replace('STATE-ITEMS-PLACEHOLDER',f'{str(items_length)} {'items' if items_length > 1 else 'item'}')

        kernel_items = ParserBuilder.get_kernel_items_lr0(state,g)
        kernel_items_html_details = ['\t'*8 + f'<li>{item}</li>' for item in kernel_items]
        non_kernel_items_html_details = ['\t'*8 + f'<li>{item}</li>' for item in state.items if not item in kernel_items]
        
        state_detail_html = state_detail_html.replace('STATE-KERNEL-ITEMS-PLACEHOLDER','\n'.join(kernel_items_html_details))
        state_detail_html = state_detail_html.replace('STATE-NON-KERNEL-ITEMS-PLACEHOLDER','\n'.join(non_kernel_items_html_details))

        states_details.append(state_detail_html)

    html = html.replace('<!-- STATES-DETAILS-PLACEHOLDER -->','\n'.join(states_details))

    return html