let A = database('json').macro('host')
| union * as A
| extend name='A'
;
let B = database('json').macro('network')
| union * as B
| extend name='B'
;
let C = database('json').macro('host')
| union * as C
| extend name='C'
;
let D = database('json').macro('network')
| extend name='D', source.ip = toip4(source.ip)
| where source.ip == ip4subnet('192.168.0.0/16')
;
union A, B, C, D
| project ['@timestamp'], original_name=name, src_ip=toip4(source.ip), src_port=source.port, dest_ip=toip4(destination.ip), dest_port=destination.port
| union * as final
| summarize count() by original_name
