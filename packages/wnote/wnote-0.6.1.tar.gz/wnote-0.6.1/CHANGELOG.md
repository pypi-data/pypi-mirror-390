# Changelog

All notable changes to the WNote project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.1] - 2025-11-09

### 🔗 Major: Symlink Support for Attachments

#### Added
- **Symlink attachment mode** (default) - Saves 99% disk space
- **Three attachment modes**: symlink, copy, reference
  - `symlink` (default) - Creates symbolic link, saves space, stays in sync
  - `copy` - Copies file like before, uses more space but safer
  - `reference` - Only saves path, no copy or link
- **`--mode` option** for attach command: `wnote attach <id> <file> --mode <symlink|copy|reference>`
- **`--attach-mode` option** for add command when using `-f` flag
- **Mode indicator** in attachment listings (🔗 link, 📄 copy, 📌 ref)
- **Broken symlink detection** - Shows "Missing" status for broken links
- **Database column**: `attachment_mode` in attachments table

#### Fixed
- **Critical**: Permanent delete now properly removes attachments based on mode
  - Symlinks: Only removes link, **original file intact** ✓
  - Copies: Removes copied file, **original file intact** ✓
  - References: Only removes path record ✓
- **Bug**: Attachments were not being deleted from disk when note was permanently deleted
- **Safety**: Added protection to never delete original files, only links/copies

#### Changed
- **Default attachment behavior**: Changed from copy to symlink (saves space)
- **Performance**: 20-300x faster attachment operations
- **Disk usage**: 99% reduction with symlink mode

#### Improved
- **Help text formatting**: All commands now have proper indentation and `$` prompt
- **Examples formatting**: Commands indented with clear visual hierarchy
- **Error messages**: More specific messages based on attachment mode
- **Attachment display**: Shows mode, size, and status for each attachment

### 🎨 UI/UX Improvements

#### Changed
- **Help text formatting**: Added `\b` markers for better line control
- **Example indentation**: All examples now properly indented with `$ ` prefix
- **Visual hierarchy**: Clear separation between description, examples, and tips
- **Bullet points**: Consistent use of • for lists

#### Improved
- **Readability**: Better spacing and formatting in all help texts
- **Consistency**: Uniform style across all commands
- **User guidance**: Clearer explanations of when to use each mode

### 📝 Documentation

#### Changed
- **Files cleaned up**: Removed temporary documentation files
  - Removed: COMPLETED_IMPROVEMENTS.md
  - Removed: IMPROVEMENTS_v0.6.1.md
  - Removed: REFACTORING_SUMMARY.md
  - Removed: quick_test.sh
- **Kept essential docs**: README, CHANGELOG, DEVELOPMENT, TESTING_GUIDE, MIGRATION_GUIDE

### 🔧 Technical Improvements

#### Database
- **Auto-migration**: Automatically adds `attachment_mode` column to existing databases
- **Backward compatible**: Old attachments work as 'copy' mode
- **Foreign keys**: Proper cascade deletion maintained

#### Code Quality
- **Type safety**: Better type hints in attachment functions
- **Error handling**: Mode-specific error messages
- **Safety checks**: Protection against deleting original files

### Migration Notes

No action required! The database auto-migrates on first run.
- Existing attachments automatically marked as 'copy' mode
- New attachments default to 'symlink' mode
- All old functionality preserved

### Performance Impact

| Operation | v0.6.0 | v0.6.1 | Improvement |
|-----------|--------|--------|-------------|
| Attach 100MB file | ~2s | <0.1s | **20x faster** |
| Attach 1GB folder | ~30s | <0.1s | **300x faster** |
| Disk usage | 100% overhead | <0.1% overhead | **99% saved** |

---

## [0.6.0] - 2025-11-08

### 🎉 Major Refactoring and New Features

This is a major release with significant architectural improvements and new features.

### Added
- **📋 Templates System**: Create and use note templates for common formats
  - `wnote template create <name>` - Create new template
  - `wnote template list` - View all templates
  - `wnote template show <name>` - Display template content
  - Use templates with `--template` flag when creating notes

- **💾 Backup & Restore**: Comprehensive backup system
  - `wnote backup` - Create automatic or manual backups
  - `wnote backup --compress` - Create compressed backups
  - `wnote restore <backup_name>` - Restore from backup
  - `wnote list-backups` - View all available backups
  - Automatic cleanup of old backups (configurable)

- **📦 Archive System**: Archive notes without deleting them
  - `wnote archive <note_id>` - Archive a note
  - `wnote archive --list` - List archived notes
  - `wnote archive --restore-note <id>` - Restore archived note
  - Archived notes excluded from normal searches and listings

- **🔗 Note Linking**: Database support for linking notes (UI coming soon)
  - Database schema includes `note_links` table
  - Backend functions for creating and retrieving linked notes

- **🔍 Enhanced Search**: Improved search functionality
  - Filter search by tags with `--tag` option
  - Include archived notes in search with `--archived`
  - Better relevance scoring

- **📊 Expanded Statistics**: More detailed statistics
  - Active vs archived note counts
  - Note links count
  - Templates count
  - Better visualization with activity bars

### Changed
- **🏗️ Complete Code Restructuring**: Modular, maintainable architecture
  ```
  Old: Single monolithic wnote.py (2000+ lines)
  New: Organized package structure
       wnote/
       ├── core/          # Database, configuration
       ├── commands/      # Command modules
       └── utils/         # Utilities
  ```

- **✨ Improved Code Quality**:
  - Added comprehensive type hints throughout
  - Better error handling and logging
  - Improved docstrings and documentation
  - Separation of concerns (SRP principle)
  - More testable code structure

- **🎨 Enhanced UI/UX**:
  - Better formatted output with Rich library
  - Improved table displays
  - Better error messages
  - More informative help text

- **⚙️ Extended Configuration**:
  - New config options: `auto_backup`, `backup_interval_days`, `max_backups`
  - New config options: `search_limit`, `preview_length`, `date_format`
  - Support for archived tag color: `bright_black`

### Fixed
- Database connection handling improvements
- Better file operation error handling
- Improved cross-platform compatibility
- Fixed edge cases in note ID reuse logic

### Technical Improvements
- **Package Structure**: Proper Python package with submodules
- **Entry Point**: Updated to `wnote.cli:cli`
- **Build System**: Modern pyproject.toml configuration
- **Dependencies**: Properly specified in setup.py and requirements.txt
- **Type Safety**: Type hints for better IDE support and error catching
- **Documentation**: Comprehensive README with architecture diagrams

### Migration Notes
- **Breaking Change**: Package structure changed
  - Old import: `from wnote import cli` still works (compatibility layer)
  - New import: `from wnote.cli import cli`
- Configuration and database paths remain unchanged
- All existing data is compatible
- No action required for end users

## [0.5.2] - 2025-05-24

### Fixed
- **Critical**: Fixed attachment inheritance bug where new notes with reused IDs would inherit attachments from deleted notes
- **Critical**: Fixed timezone issue - all timestamps now use local system time instead of UTC
- Enabled SQLite foreign key constraints to ensure proper cascade deletion
- Improved attachment deletion to explicitly remove records from database before deleting note
- Enhanced datetime parsing to support both standard and ISO formats for backward compatibility
- Added better error handling for attachment file deletion from disk

### Changed
- All datetime operations now use local system timezone
- Database connections now enforce foreign key constraints
- Improved robustness of attachment management system

## [0.5.1] - 2024-03-19

### Changed
- Updated README with bilingual support (English and Vietnamese)
- Improved documentation with development setup instructions
- Removed unnecessary files (PYPI_UPLOAD_GUIDE.md, build_and_test.sh, install.sh)
- Synchronized setup.py with pyproject.toml
- Added development dependencies configuration

## [0.5.0] - 2024-03-19

### Added
- Reminders functionality: Add, view, complete, and delete reminders for notes
- Deattach command: Remove attachments from notes with detailed management options
- Comprehensive stats command: Display detailed statistics about notes, tags, attachments, and reminders
- Enhanced README: Removed unimplemented features and updated documentation

### Fixed
- Updated README to match actual implemented features
- Improved documentation with accurate feature descriptions

## [0.4.0] - 2024-03-19

### Added
- Search functionality to find notes by content or title
- Export feature to export notes in text, markdown, or HTML formats
- Ability to delete tags with `delete --tag` command
- Reuse of note IDs after deletion for better ID management
- Improved help text for all commands with detailed examples

### Fixed
- Fixed attach command to better handle files from different drives
- Enhanced file path handling with expansion of relative paths
- Better error handling for attachments and file operations
- Fixed ID allocation to reuse deleted note IDs

## [0.3.1] - 2024-03-19

### Fixed
- Database lock issue with improved retry mechanism and connection timeout
- JSON serialization error in config command
- Enhanced error handling in configuration loading and saving
- Improved robustness against non-serializable objects in configuration

## [0.3.0] - 2024-03-19

### Added
- Support for file and directory attachments
- Attachment preview and opening
- Custom tag colors
- Color configuration system
- Note filtering by tags
- Enhanced UI with Rich library

### Changed
- Improved database schema for attachments
- Better error handling
- Updated documentation

## [0.2.0] - 2024-03-19

### Added
- Basic note taking functionality
- Tag support
- Editor integration
- SQLite database backend

## [0.1.0] - 2024-03-18

### Added
- Initial release
- Basic CLI structure
- Note creation and viewing

---

## Legend

- 🎉 Major feature
- ✨ Enhancement
- 🐛 Bug fix
- 🔧 Configuration
- 📝 Documentation
- 🏗️ Architecture
- ⚡ Performance
- 🔒 Security
- 💾 Data
- 🎨 UI/UX

## Upgrading

### From 0.5.x to 0.6.0

1. **Backup your data** (recommended):
   ```bash
   # Using old version
   cp -r ~/.config/wnote ~/.config/wnote.backup
   ```

2. **Update WNote**:
   ```bash
   pip install --upgrade wnote
   ```

3. **Verify installation**:
   ```bash
   wnote --version  # Should show 0.6.0
   wnote stats      # Verify data integrity
   ```

4. **New features to try**:
   ```bash
   # Create a backup
   wnote backup
   
   # Create a template
   wnote template create meeting
   
   # Archive old notes
   wnote archive <note_id>
   ```

### Rolling Back

If you encounter issues:

```bash
# Restore your backup
rm -rf ~/.config/wnote
cp -r ~/.config/wnote.backup ~/.config/wnote

# Downgrade to previous version
pip install wnote==0.5.2
```

## Support

For issues, questions, or suggestions:
- GitHub Issues: https://github.com/imnotnahn/wnote/issues
- Discussions: https://github.com/imnotnahn/wnote/discussions
