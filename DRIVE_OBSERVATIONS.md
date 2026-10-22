# Bounded Drive state observation

`observe_drive_file_state` reads one exact Drive ID under the caller's existing
Google authorization. It returns only ID, revision, file kind, trash state and
`canEdit` / `canTrash` / `canUntrash` flags. It never follows shortcuts or reads
content, names, owners or permission lists. Provider fields are allowlisted.

Missing metadata stays null. Missing access is not proof that a file is absent.
A capability flag does not establish application permission or restoration of
prior content. The companion Celemine grammar PR uses this endpoint as a
separately governed child Action before and after supported updates; it does not
add rollback or business retries.

Local validation uses mocked Google services. Live provider behavior and
production deployment remain separate checks.
