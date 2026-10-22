from unittest.mock import Mock
import pytest
from gdrive.drive_tools import observe_drive_file_state, DRIVE_OBSERVATION_FIELDS


def unwrap(tool):
    fn = tool.fn if hasattr(tool, 'fn') else tool
    while hasattr(fn, '__wrapped__'):
        fn = fn.__wrapped__
    return fn


@pytest.mark.asyncio
async def test_observation_reads_one_exact_id_and_allowlists_metadata():
    service = Mock()
    service.files().get().execute.return_value = {
        'id': 'target', 'version': '12', 'mimeType': 'text/plain', 'trashed': True,
        'name': 'PRIVATE', 'owners': [{'emailAddress': 'private@example.com'}],
        'capabilities': {'canEdit': True, 'canUntrash': False, 'canShare': True},
    }
    result = await unwrap(observe_drive_file_state)(service, 'actor@example.com', 'target')
    assert service.files().get.call_args.kwargs == {
        'fileId': 'target', 'fields': DRIVE_OBSERVATION_FIELDS, 'supportsAllDrives': True,
    }
    assert result == {'version': 1, 'file_id': 'target', 'revision': '12', 'kind': 'file',
                      'trashed': True, 'canEdit': True, 'canTrash': None, 'canUntrash': False}
    assert 'PRIVATE' not in str(result)
    service.files().update.assert_not_called()
    service.files().get_media.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize('mime,kind', [('application/vnd.google-apps.folder', 'folder'),
                                      ('application/vnd.google-apps.shortcut', 'shortcut')])
async def test_observation_never_follows_shortcuts_or_asserts_missing_capabilities(mime, kind):
    service = Mock()
    service.files().get().execute.return_value = {'id': 'target', 'mimeType': mime}
    result = await unwrap(observe_drive_file_state)(service, 'actor@example.com', 'target')
    assert result['kind'] == kind
    assert result['revision'] is None
    assert result['canUntrash'] is None
    assert service.files().get.call_count == 2  # mock setup plus exactly one actual request


@pytest.mark.asyncio
async def test_provider_error_is_not_absence():
    service = Mock()
    service.files().get().execute.side_effect = RuntimeError('denied or missing')
    with pytest.raises(RuntimeError):
        await unwrap(observe_drive_file_state)(service, 'actor@example.com', 'target')
