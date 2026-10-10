# Local cleanup plan

1. Inventory roots, metadata, symlinks, content hashes and direct rule references.
2. Record the exact removal/consolidation list. Create a durable private backup
   area outside every Skill discovery root before mutations.
3. Revalidate each original fingerprint; move removable entries and archive
   containers into backup storage. Move the chosen Graphify tree into `.agents`.
   Symlink cleanup removes/moves links only, never their source targets.
4. Verify all changed/retained trees and protected native config/system/plugin
   roots. Check metadata and absence of unresolved duplicate identities in the
   Codex user roots; keep separate host installations.
5. Apply native Trellis check to the operation, save receipts and restore paths.
   No full test suite, unrelated package update, application reload or Git action.

Selected entries are backed up rather than irreversibly erased. Fresh Skill
discovery remains an application-level observation after the filesystem checks.
