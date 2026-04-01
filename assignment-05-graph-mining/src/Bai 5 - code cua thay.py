
import pm4py

import pandas as pd

# 1. Khởi tạo dữ liệu (Dựa trên kịch bản Building Inspection đã tạo ở trên)

event_data = {

    'case:concept:name': [

        '1', '1', '1', '1', '1',

        '2', '2',

        '3', '3', '3', '3', '3', '3',

        '4', '4', '4', '4', '4',

        '5', '5'

    ],

    'concept:name': [

        'Inspect Building', 'Complete Inspection', 'Send Email Notification', 'Prepare Invoice', 'Generate Invoice',

        'Inspect Building', 'Inspection Cancelled',

        'Inspect Building', 'Complete Inspection', 'Send Email Notification', 'Inspect Building', 'Complete Inspection',
        'Generate Invoice',

        'Inspect Building', 'Complete Inspection', 'Send Email Notification', 'Prepare Invoice', 'Generate Invoice',

        'Inspect Building', 'Inspection Cancelled'

    ],

    'time:timestamp': pd.to_datetime([

        '2026-03-17 08:00', '2026-03-17 09:00', '2026-03-17 09:10', '2026-03-17 10:00', '2026-03-17 10:30',

        '2026-03-17 08:15', '2026-03-17 08:45',

        '2026-03-17 08:30', '2026-03-17 09:30', '2026-03-17 09:40', '2026-03-17 11:00', '2026-03-17 12:00',
        '2026-03-17 12:30',

        '2026-03-18 08:00', '2026-03-18 09:00', '2026-03-18 09:15', '2026-03-18 10:00', '2026-03-18 10:45',

        '2026-03-18 08:30', '2026-03-18 09:00'

    ])

}

df = pd.DataFrame(event_data)

# 2. Khám phá mô hình bằng Inductive Miner

# Thuật toán này rất mạnh trong việc phát hiện loop và branch từ log

net, im, fm = pm4py.discover_petri_net_inductive(df,

                                                 case_id_key='case:concept:name',

                                                 activity_key='concept:name',

                                                 timestamp_key='time:timestamp')

# 3. Chuyển đổi Petri Net vừa khám phá sang định dạng BPMN

bpmn_graph = pm4py.convert_to_bpmn(net, im, fm)

# 4. Trực quan hóa sơ đồ BPMN

pm4py.view_bpmn(bpmn_graph)

# 5. (Tùy chọn) Xuất file để kiểm tra cấu trúc XML

# pm4py.write_bpmn(bpmn_graph, "building_inspection_model.bpmn")


