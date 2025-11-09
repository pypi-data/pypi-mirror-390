/**
 * @title File Download Via Curl.EXE
 * @author Florian Roth (Nextron Systems)
 * @id 9a517fca-4ba3-4629-9278-a68694697b81
 * 
 * @status test
 * @level medium
 * @schedule 0 * * * *
 * @description Detects file download using curl.exe
 * 
 * @tags
 * - attack.command-and-control
 * - attack.t1105
 * - detection.threat-hunting
 * 
 * @falsepositives
 * - Scripts created by developers and admins
 * - Administrative activity
 * - The "\Git\usr\bin\sh.exe" process uses the "--output" flag to download a specific file in the temp directory with the pattern "gfw-httpget-xxxxxxxx.txt "
 * 
 * @references
 * - https://web.archive.org/web/20200128160046/https://twitter.com/reegun21/status/1222093798009790464
 * 
 * @related
 * - {'id': 'bbeaed61-1990-4773-bf57-b81dbad7db2d', 'type': 'derived'}
 * - {'id': 'e218595b-bbe7-4ee5-8a96-f32a24ad3468', 'type': 'derived'}
 * 
 * @date 2022-07-05
 * @modified 2023-02-21
 */
product('windows').category('process_creation')
| where Image endswith '\\curl.exe' or Product == 'The curl executable'
| where CommandLine contains_any (' -O', '--remote-name', '--output')
| union *
| project scot_res=scot4()