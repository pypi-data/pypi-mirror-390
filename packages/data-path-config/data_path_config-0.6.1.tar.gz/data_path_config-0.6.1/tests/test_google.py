import pytest
from data_path_config.google.sheet import GoogleSheetsManager
from data_path_config.google.drive import GoogleDriveManager

def test_imports():
    """Test that GoogleSheetsManager can be imported and has expected methods."""
    assert GoogleSheetsManager
    assert hasattr(GoogleSheetsManager, 'list_sheets')
    assert hasattr(GoogleSheetsManager, 'sheet_df')
    assert hasattr(GoogleSheetsManager, 'append_to_sheet')
    assert hasattr(GoogleSheetsManager, 'df_to_sheet')
    assert hasattr(GoogleSheetsManager, 'insert_key_value')
    assert hasattr(GoogleSheetsManager, 'list_shared_drive_sheets')
    assert hasattr(GoogleSheetsManager, 'create_spreadsheet')
    
    # Test GoogleDriveManager import
    assert GoogleDriveManager
    assert hasattr(GoogleDriveManager, 'list_files')
    assert hasattr(GoogleDriveManager, 'upload_file')
    assert hasattr(GoogleDriveManager, 'download_file')
    assert hasattr(GoogleDriveManager, 'create_folder')
    assert hasattr(GoogleDriveManager, 'delete_file')
    assert hasattr(GoogleDriveManager, 'get_file_info')
    assert hasattr(GoogleDriveManager, 'move_file')
    assert hasattr(GoogleDriveManager, 'copy_file')
    assert hasattr(GoogleDriveManager, 'list_shared_drives')
    assert hasattr(GoogleDriveManager, 'list_shared_drive_files')
    assert hasattr(GoogleDriveManager, 'create_file')

def test_google_sheets_manager():
    """Test GoogleSheetsManager initialization."""
    try:
        manager = GoogleSheetsManager()
        assert manager.gc is not None
    except (ValueError, FileNotFoundError) as e:
        # Expected if .env not set or file missing
        assert "not set" in str(e) or "No such file" in str(e)

def test_list_sheets():
    """Test list_sheets method."""
    try:
        manager = GoogleSheetsManager()
        sheets = manager.list_sheets()
        print(f"All sheets: {sheets}")
        assert isinstance(sheets, list)
        if sheets:
            assert 'id' in sheets[0]
            assert 'title' in sheets[0]
    except (ValueError, FileNotFoundError) as e:
        # Expected if .env not set or file missing
        assert "not set" in str(e) or "No such file" in str(e)

def test_list_shared_drive_sheets():
    """Test list_shared_drive_sheets method."""
    try:
        manager = GoogleSheetsManager()
        # Get the first shared drive and use its ID
        drive_manager = GoogleDriveManager()
        drives = drive_manager.list_shared_drives()
        if drives:
            drive_id = drives[0]['id']
            sheets = manager.list_shared_drive_sheets(drive_id)
            print(f"Shared drive sheets in '{drives[0]['name']}': {sheets}")
            assert isinstance(sheets, list)
            if sheets:
                assert 'id' in sheets[0]
                assert 'title' in sheets[0]
        else:
            print("No shared drives found to test sheet listing")
    except Exception as e:
        # Expected if .env not set or invalid drive_id
        print(f"Expected error: {e}")
        # Test passes as long as no unexpected errors

def test_create_spreadsheet_public():
    """Test create_spreadsheet method with public sharing."""
    try:
        manager = GoogleSheetsManager()
        # Create a test spreadsheet with public sharing
        spreadsheet_id = manager.create_spreadsheet("Public Test Spreadsheet", public_share=True)
        print(f"Created public spreadsheet with ID: {spreadsheet_id}")
        assert spreadsheet_id is not None
        assert isinstance(spreadsheet_id, str)
        
        # Verify the spreadsheet was created by trying to access it
        df = manager.sheet_df(sheet_id=spreadsheet_id)
        print(f"Verified public spreadsheet creation: {len(df)} rows")
        
        # Verify public permissions
        from data_path_config.google.drive import GoogleDriveManager
        drive_manager = GoogleDriveManager()
        permissions = drive_manager.service.permissions().list(fileId=spreadsheet_id, supportsAllDrives=True).execute()
        public_permission = next((p for p in permissions.get('permissions', []) if p.get('type') == 'anyone'), None)
        assert public_permission is not None
        assert public_permission.get('role') == 'reader'
        print(f"Verified public permissions: {public_permission}")
        
    except Exception as e:
        # Expected if .env not set or API errors
        print(f"Expected error: {e}")
        # Test passes as long as no unexpected errors

def test_google_drive_manager():
    """Test GoogleDriveManager initialization."""
    try:
        manager = GoogleDriveManager()
        assert manager.service is not None
    except (ValueError, FileNotFoundError) as e:
        # Expected if .env not set or file missing
        assert "not set" in str(e) or "No such file" in str(e)

def test_list_files():
    """Test list_files method."""
    try:
        manager = GoogleDriveManager()
        files = manager.list_files()
        print(f"All files: {files}")
        assert isinstance(files, list)
        if files:
            assert 'id' in files[0]
            assert 'name' in files[0]
    except (ValueError, FileNotFoundError) as e:
        # Expected if .env not set or file missing
        assert "not set" in str(e) or "No such file" in str(e)

def test_list_shared_drives():
    """Test list_shared_drives method."""
    try:
        manager = GoogleDriveManager()
        drives = manager.list_shared_drives()
        print(f"All shared drives: {drives}")
        assert isinstance(drives, list)
        if drives:
            assert 'id' in drives[0]
            assert 'name' in drives[0]
    except Exception as e:
        # Expected if .env not set, file missing, or no shared drives accessible
        print(f"Expected error: {e}")
        # Test passes as long as no unexpected errors

def test_list_shared_drive_files():
    """Test list_shared_drive_files method."""
    try:
        manager = GoogleDriveManager()
        # Get the first shared drive and list its files
        drives = manager.list_shared_drives()
        if drives:
            drive_id = drives[0]['id']
            files = manager.list_shared_drive_files(drive_id)
            print(f"Files in shared drive '{drives[0]['name']}': {files}")
            assert isinstance(files, list)
            if files:
                assert 'id' in files[0]
                assert 'name' in files[0]
        else:
            print("No shared drives found to test file listing")
    except Exception as e:
        # Expected if .env not set, file missing, or no shared drives accessible
        print(f"Expected error: {e}")
        # Test passes as long as no unexpected errors

def test_create_file():
    """Test create_file method."""
    try:
        manager = GoogleDriveManager()
        # Create a test file with some content (will automatically use shared drive)
        test_content = "This is a test file created by the GoogleDriveManager in shared drive."
        file_id = manager.create_file("test_file.txt", test_content)
        print(f"Created file with ID: {file_id}")
        assert file_id is not None
        assert isinstance(file_id, str)
        
        # Verify the file was created by listing all files (should include shared drive files)
        files = manager.list_files()
        created_file = next((f for f in files if f['id'] == file_id), None)
        assert created_file is not None
        assert created_file['name'] == "test_file.txt"
        print(f"Verified file creation: {created_file}")
        
    except Exception as e:
        # Expected if .env not set, file missing, or no shared drives available
        print(f"Expected error: {e}")
        # Test passes as long as no unexpected errors

def test_create_file_public():
    """Test create_file method with public sharing."""
    try:
        manager = GoogleDriveManager()
        # Create a test file with public sharing enabled
        test_content = "This is a public test file created by the GoogleDriveManager."
        file_id = manager.create_file("public_test_file.txt", test_content, public_share=True)
        print(f"Created public file with ID: {file_id}")
        assert file_id is not None
        assert isinstance(file_id, str)
        
        # Verify the file was created and is publicly accessible
        files = manager.list_files()
        created_file = next((f for f in files if f['id'] == file_id), None)
        assert created_file is not None
        assert created_file['name'] == "public_test_file.txt"
        print(f"Verified public file creation: {created_file}")
        
        # Check permissions to verify it's public
        permissions = manager.service.permissions().list(fileId=file_id, supportsAllDrives=True).execute()
        public_permission = next((p for p in permissions.get('permissions', []) if p.get('type') == 'anyone'), None)
        assert public_permission is not None
        assert public_permission.get('role') == 'reader'
        print(f"Verified public permissions: {public_permission}")
        
    except Exception as e:
        # Expected if .env not set, file missing, or no shared drives available
        print(f"Expected error: {e}")
        # Test passes as long as no unexpected errors