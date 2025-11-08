"""
测试三个核心 MCP 工具的功能
"""

import os
import json
import tempfile
from unittest.mock import patch, MagicMock
from pathlib import Path

import pytest

from devlake_mcp.server import record_session_impl, before_edit_file_impl, after_edit_file_impl
from devlake_mcp.utils import get_temp_file_path


class TestRecordSession:
    """测试 recordSession 工具"""

    @patch('devlake_mcp.server.DevLakeClient')
    @patch('devlake_mcp.server.get_git_info')
    @patch('devlake_mcp.server.get_git_repo_path')
    def test_record_session_with_auto_session_id(
        self,
        mock_get_repo_path,
        mock_get_git_info,
        mock_client_class
    ):
        """测试自动生成 session_id"""
        # Mock Git 信息
        mock_get_git_info.return_value = {
            'git_branch': 'main',
            'git_commit': 'abc123def456',
            'git_author': 'Test User',
            'git_email': 'test@example.com'
        }
        mock_get_repo_path.return_value = 'yourorg/devlake'

        # Mock API 客户端
        mock_client = MagicMock()
        mock_client.post.return_value = {'success': True}
        mock_client_class.return_value = mock_client

        # 调用工具
        result = record_session_impl()

        # 验证结果
        assert result['success'] is True
        assert 'session_id' in result
        assert len(result['session_id']) == 36  # UUID 长度
        assert result['git_info']['git_branch'] == 'main'
        assert result['git_info']['git_author'] == 'Test User'

        # 验证 API 调用
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert call_args[0][0] == '/sessions'
        session_data = call_args[0][1]
        assert session_data['git_repo_path'] == 'yourorg/devlake'
        assert session_data['project_name'] == 'devlake'

    @patch('devlake_mcp.server.DevLakeClient')
    @patch('devlake_mcp.server.get_git_info')
    @patch('devlake_mcp.server.get_git_repo_path')
    def test_record_session_with_provided_session_id(
        self,
        mock_get_repo_path,
        mock_get_git_info,
        mock_client_class
    ):
        """测试使用提供的 session_id"""
        mock_get_git_info.return_value = {
            'git_branch': 'main',
            'git_commit': 'abc123',
            'git_author': 'User',
            'git_email': 'user@example.com'
        }
        mock_get_repo_path.return_value = 'org/repo'

        mock_client = MagicMock()
        mock_client.post.return_value = {'success': True}
        mock_client_class.return_value = mock_client

        # 使用提供的 session_id
        custom_session_id = 'my-session-123'
        result = record_session_impl(session_id=custom_session_id)

        assert result['success'] is True
        assert result['session_id'] == custom_session_id

    @patch('devlake_mcp.server.DevLakeClient')
    def test_record_session_api_error(self, mock_client_class):
        """测试 API 调用失败的情况"""
        mock_client = MagicMock()
        mock_client.post.side_effect = Exception('API connection failed')
        mock_client_class.return_value = mock_client

        result = record_session_impl()

        assert result['success'] is False
        assert 'error' in result
        assert 'API connection failed' in result['error']


class TestBeforeEditFile:
    """测试 beforeEditFile 工具"""

    def test_before_edit_file_existing_file(self, tmp_path):
        """测试记录已存在文件的快照"""
        # 创建测试文件
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')\n")

        session_id = 'test-session'
        result = before_edit_file_impl(session_id, [str(test_file)])

        # 验证结果
        assert result['success'] is True
        assert result['session_id'] == session_id
        assert str(test_file) in result['files_snapshot']

        snapshot = result['files_snapshot'][str(test_file)]
        assert snapshot['exists'] is True
        assert snapshot['line_count'] == 1
        assert snapshot['size'] > 0

        # 验证临时文件已创建
        temp_file = get_temp_file_path(session_id, str(test_file))
        assert os.path.exists(temp_file)

        # 验证临时文件内容
        with open(temp_file, 'r') as f:
            temp_data = json.load(f)
            assert temp_data['content'] == "print('hello')\n"

        # 清理
        os.remove(temp_file)

    def test_before_edit_file_new_file(self):
        """测试记录不存在的文件（新建文件）"""
        session_id = 'test-session'
        new_file = '/tmp/nonexistent_file.py'

        result = before_edit_file_impl(session_id, [new_file])

        assert result['success'] is True
        snapshot = result['files_snapshot'][new_file]
        assert snapshot['exists'] is False
        assert snapshot['line_count'] == 0

    def test_before_edit_file_sensitive_file(self):
        """测试敏感文件被跳过"""
        session_id = 'test-session'
        sensitive_file = '/path/to/.env'

        result = before_edit_file_impl(session_id, [sensitive_file])

        assert result['success'] is True
        snapshot = result['files_snapshot'][sensitive_file]
        assert snapshot['skipped'] is True
        assert 'Sensitive' in snapshot['reason']


class TestAfterEditFile:
    """测试 afterEditFile 工具"""

    @patch('devlake_mcp.server.DevLakeClient')
    @patch('devlake_mcp.server.get_git_info')
    @patch('devlake_mcp.server.get_git_repo_path')
    @patch('devlake_mcp.server.get_git_root')
    def test_after_edit_file_with_changes(
        self,
        mock_get_git_root,
        mock_get_repo_path,
        mock_get_git_info,
        mock_client_class,
        tmp_path
    ):
        """测试上传文件变更"""
        # 创建测试文件
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')\n")

        # Mock Git 信息
        mock_get_git_info.return_value = {
            'git_branch': 'main',
            'git_commit': 'abc123',
            'git_author': 'Test User',
            'git_email': 'test@example.com'
        }
        mock_get_repo_path.return_value = 'org/repo'
        mock_get_git_root.return_value = str(tmp_path)

        # Mock API 客户端
        mock_client = MagicMock()
        mock_client.post.return_value = {'success': True}
        mock_client_class.return_value = mock_client

        # 先调用 before_edit_file
        session_id = 'test-session'
        before_edit_file_impl(session_id, [str(test_file)])

        # 修改文件
        test_file.write_text("print('hello')\nprint('world')\n")

        # 调用 after_edit_file
        result = after_edit_file_impl(session_id, [str(test_file)])

        # 验证结果
        assert result['success'] is True
        assert result['uploaded_count'] == 1
        assert len(result['changes']) == 1

        change = result['changes'][0]
        assert change['file_path'] == 'test.py'
        assert change['change_type'] == 'edit'
        assert change['file_type'] == 'py'

        # 验证 API 调用
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert call_args[0][0] == '/file-changes'

        # 验证临时文件已清理
        temp_file = get_temp_file_path(session_id, str(test_file))
        assert not os.path.exists(temp_file)

    @patch('devlake_mcp.server.DevLakeClient')
    @patch('devlake_mcp.server.get_git_info')
    @patch('devlake_mcp.server.get_git_repo_path')
    @patch('devlake_mcp.server.get_git_root')
    def test_after_edit_file_create_file(
        self,
        mock_get_git_root,
        mock_get_repo_path,
        mock_get_git_info,
        mock_client_class,
        tmp_path
    ):
        """测试新建文件的情况"""
        test_file = tmp_path / "new_file.py"

        mock_get_git_info.return_value = {
            'git_branch': 'main',
            'git_commit': 'abc123',
            'git_author': 'User',
            'git_email': 'user@example.com'
        }
        mock_get_repo_path.return_value = 'org/repo'
        mock_get_git_root.return_value = str(tmp_path)

        mock_client = MagicMock()
        mock_client.post.return_value = {'success': True}
        mock_client_class.return_value = mock_client

        # 调用 before_edit_file（文件不存在）
        session_id = 'test-session'
        before_edit_file_impl(session_id, [str(test_file)])

        # 创建文件
        test_file.write_text("print('new file')\n")

        # 调用 after_edit_file
        result = after_edit_file_impl(session_id, [str(test_file)])

        assert result['success'] is True
        assert result['changes'][0]['change_type'] == 'create'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
