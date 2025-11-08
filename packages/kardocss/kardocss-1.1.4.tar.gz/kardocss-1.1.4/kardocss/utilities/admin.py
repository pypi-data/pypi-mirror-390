"""
Admin Panel Utilities for KardoCSS

Specific utilities for administrative interfaces.
"""

def generate_admin_utilities():
    """Generate admin-specific utility classes"""
    css = []
    
    # Sidebar utilities
    css.append("/* Admin Sidebar */")
    css.append(".sidebar { width: 16rem; height: 100vh; position: sticky; top: 0; }")
    css.append(".sidebar-mobile { position: fixed; left: 0; top: 0; z-index: 40; transform: translateX(-100%); transition: transform 0.3s; }")
    css.append(".sidebar-mobile.open { transform: translateX(0); }")
    css.append(".sidebar-item { display: block; padding: 0.5rem 1rem; border-radius: 0.375rem; transition: background 0.2s; }")
    css.append(".sidebar-item:hover { background: #f3f4f6; }")
    css.append(".sidebar-item.active { background: #3b82f6; color: white; }")
    
    # Table utilities
    css.append("\n/* Admin Tables */")
    css.append(".table-admin { width: 100%; border-collapse: collapse; }")
    css.append(".table-admin th { text-align: left; padding: 0.75rem; background: #f9fafb; font-weight: 600; border-bottom: 2px solid #e5e7eb; }")
    css.append(".table-admin td { padding: 0.75rem; border-bottom: 1px solid #e5e7eb; }")
    css.append(".table-admin tr:hover { background: #f9fafb; }")
    css.append(".table-admin tr:last-child td { border-bottom: none; }")
    
    # Stats card utilities
    css.append("\n/* Admin Stats Cards */")
    css.append(".stat-card { background: white; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }")
    css.append(".stat-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); transition: all 0.2s; }")
    css.append(".stat-value { font-size: 2rem; font-weight: 700; margin: 0.5rem 0; }")
    css.append(".stat-label { font-size: 0.875rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; }")
    
    # Badge variants
    css.append("\n/* Admin Badges */")
    css.append(".badge-admin { background: #3b82f6; }")
    css.append(".badge-author { background: #10b981; }")
    css.append(".badge-user { background: #6b7280; }")
    css.append(".badge-published { background: #10b981; }")
    css.append(".badge-draft { background: #f59e0b; }")
    css.append(".badge-pending { background: #ef4444; }")
    
    # Action buttons
    css.append("\n/* Admin Action Buttons */")
    css.append(".btn-action { padding: 0.25rem 0.75rem; font-size: 0.875rem; border-radius: 0.25rem; }")
    css.append(".btn-edit { background: #3b82f6; color: white; }")
    css.append(".btn-edit:hover { background: #2563eb; }")
    css.append(".btn-delete { background: #ef4444; color: white; }")
    css.append(".btn-delete:hover { background: #dc2626; }")
    css.append(".btn-view { background: #6b7280; color: white; }")
    css.append(".btn-view:hover { background: #4b5563; }")
    
    # Header utilities
    css.append("\n/* Admin Header */")
    css.append(".admin-header { background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); position: sticky; top: 0; z-index: 50; }")
    css.append(".admin-header-content { display: flex; align-items: center; justify-content: space-between; padding: 1rem 1.5rem; }")
    
    # Content area
    css.append("\n/* Admin Content */")
    css.append(".admin-content { flex: 1; padding: 1.5rem; background: #f9fafb; min-height: 100vh; }")
    css.append(".admin-container { max-width: 1280px; margin: 0 auto; }")
    
    # Form utilities
    css.append("\n/* Admin Forms */")
    css.append(".form-group { margin-bottom: 1rem; }")
    css.append(".form-label { display: block; font-weight: 500; margin-bottom: 0.5rem; color: #374151; }")
    css.append(".form-input { width: 100%; padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; }")
    css.append(".form-input:focus { outline: none; border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,0.1); }")
    css.append(".form-textarea { width: 100%; padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; min-height: 8rem; }")
    css.append(".form-select { width: 100%; padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; }")
    
    # Responsive utilities
    css.append("\n/* Admin Responsive */")
    css.append("@media (max-width: 768px) {")
    css.append("  .sidebar { display: none; }")
    css.append("  .sidebar-mobile { display: block; }")
    css.append("  .admin-content { padding: 1rem; }")
    css.append("  .stat-card { margin-bottom: 1rem; }")
    css.append("  .table-admin { font-size: 0.875rem; }")
    css.append("  .table-admin th, .table-admin td { padding: 0.5rem; }")
    css.append("}")
    
    return "\n".join(css)

if __name__ == "__main__":
    print(generate_admin_utilities())
