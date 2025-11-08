/**
 * @title Headless Process Launched Via Conhost.EXE
 * @author Nasreddine Bencherchali (Nextron Systems)
 * @id 00ca75ab-d5ce-43be-b86c-55ff39c6abfc
 * 
 * @status test
 * @level medium
 * @schedule 0 * * * *
 * @description
 * Detects the launch of a child process via "conhost.exe" with the "--headless" flag.
 * The "--headless" flag hides the windows from the user upon execution.
 * 
 * @tags
 * - attack.defense-evasion
 * - attack.t1059.001
 * - attack.t1059.003
 * - detection.threat-hunting
 * 
 * @falsepositives
 * - Unknown
 * 
 * @references
 * - https://www.huntress.com/blog/fake-browser-updates-lead-to-boinc-volunteer-computing-software
 * 
 * @related
 * - {'id': '056c7317-9a09-4bd4-9067-d051312752ea', 'type': 'derived'}
 * 
 * @date 2024-07-23
 */
database('death-splunk').index('windows')
| where EventCode == 1
| where ParentImage endswith '\\conhost.exe'
| where ParentCommandLine contains '--headless'
| take 10
| extend res=scot4()
