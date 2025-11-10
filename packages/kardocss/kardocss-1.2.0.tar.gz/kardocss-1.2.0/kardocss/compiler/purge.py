"""
CSS Purger for KardoCSS
Removes unused CSS classes from the compiled CSS to reduce file size
"""

import re
from pathlib import Path
from typing import List, Set, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CSSPurger:
    """
    Purges unused CSS classes from compiled CSS.
    
    Scans HTML/JS/JSX/Vue/etc files to find used classes and removes unused ones.
    Can reduce CSS file size by 80-90% in production.
    """
    
    def __init__(self, css_content: str):
        """
        Initialize the purger with CSS content.
        
        Args:
            css_content: The full CSS content to purge
        """
        self.css_content = css_content
        self.used_classes: Set[str] = set()
        self.all_classes: Set[str] = set()
        self._extract_all_classes()
    
    def _extract_all_classes(self) -> None:
        """Extract all class names from the CSS content."""
        # Match class selectors (including escaped characters like \:)
        class_pattern = r'\.([k]-[\w-]+(?:\\:[\w-]+)*)'
        matches = re.findall(class_pattern, self.css_content)
        
        # Unescape the class names
        for match in matches:
            # Remove escape characters
            unescaped = match.replace('\\:', ':')
            self.all_classes.add(unescaped)
        
        logger.info(f"Found {len(self.all_classes)} total classes in CSS")
    
    def scan_files(self, patterns: List[str], base_dir: str = ".") -> None:
        """
        Scan files for used CSS classes.
        
        Args:
            patterns: List of glob patterns to scan (e.g., ['**/*.html', '**/*.jsx'])
            base_dir: Base directory to start scanning from
        """
        base_path = Path(base_dir)
        files_scanned = 0
        
        for pattern in patterns:
            for file_path in base_path.glob(pattern):
                if file_path.is_file():
                    self._scan_file(file_path)
                    files_scanned += 1
        
        logger.info(f"Scanned {files_scanned} files")
        logger.info(f"Found {len(self.used_classes)} used classes")
    
    def _scan_file(self, file_path: Path) -> None:
        """
        Scan a single file for CSS class usage.
        
        Args:
            file_path: Path to the file to scan
        """
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Pattern to match KardoCSS classes (k-*)
            # Matches: k-flex, k-md:flex, k-hover:bg-primary, dark:k-bg-gray-900, etc.
            patterns = [
                r'\bk-[\w-]+(?::[\w-]+)*',  # Standard classes
                r'\bdark:k-[\w-]+(?::[\w-]+)*',  # Dark mode classes
                r'\b(?:sm|md|lg|xl|2xl):k-[\w-]+',  # Responsive classes
                r'\bhover:k-[\w-]+',  # Hover classes
                r'\bfocus:k-[\w-]+',  # Focus classes
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content)
                self.used_classes.update(matches)
        
        except Exception as e:
            logger.warning(f"Error scanning {file_path}: {e}")
    
    def add_safelist(self, classes: List[str]) -> None:
        """
        Add classes to the safelist (always keep these classes).
        
        Args:
            classes: List of class names or patterns to always keep
        """
        for cls in classes:
            if '*' in cls or '?' in cls:
                # Pattern matching
                pattern = cls.replace('*', '.*').replace('?', '.')
                for css_class in self.all_classes:
                    if re.match(pattern, css_class):
                        self.used_classes.add(css_class)
            else:
                self.used_classes.add(cls)
        
        logger.info(f"Added {len(classes)} classes to safelist")
    
    def purge(self, keep_base_styles: bool = True) -> str:
        """
        Remove unused CSS classes from the CSS content.
        
        Args:
            keep_base_styles: Whether to keep base styles (resets, normalize, etc.)
        
        Returns:
            Purged CSS content
        """
        if not self.used_classes:
            logger.warning("No used classes found. CSS will be heavily purged!")
        
        lines = self.css_content.split('\n')
        output_lines = []
        
        in_rule = False
        current_rule = []
        keep_rule = False
        in_base_styles = False
        in_media_query = False
        brace_depth = 0
        
        for line in lines:
            stripped = line.strip()
            
            # Track base styles section
            if '/* Base Styles */' in line or '/* KardoCSS' in line:
                in_base_styles = True
            
            # Track media queries
            if '@media' in line:
                in_media_query = True
            
            # Track brace depth
            brace_depth += line.count('{')
            brace_depth -= line.count('}')
            
            # Check if we're starting a new rule
            if '{' in line and not in_rule:
                in_rule = True
                current_rule = [line]
                
                # Check if this rule should be kept
                if keep_base_styles and in_base_styles:
                    keep_rule = True
                elif '@' in line:  # Keep @rules like @media, @keyframes
                    keep_rule = True
                else:
                    # Check if any used class is in this selector
                    keep_rule = self._should_keep_rule(line)
            
            elif in_rule:
                current_rule.append(line)
                
                # Check if rule is complete
                if '}' in line and brace_depth == 0:
                    if keep_rule:
                        output_lines.extend(current_rule)
                    
                    # Reset
                    in_rule = False
                    current_rule = []
                    keep_rule = False
                    
                    # Check if we're leaving base styles
                    if in_base_styles and not any('@' in l for l in current_rule):
                        in_base_styles = False
            
            else:
                # Keep comments and other non-rule content
                if stripped.startswith('/*') or stripped.startswith('//') or not stripped:
                    output_lines.append(line)
        
        purged_css = '\n'.join(output_lines)
        
        # Calculate savings
        original_size = len(self.css_content)
        purged_size = len(purged_css)
        savings = ((original_size - purged_size) / original_size) * 100
        
        logger.info(f"Purged CSS: {original_size} → {purged_size} bytes ({savings:.1f}% reduction)")
        
        return purged_css
    
    def _should_keep_rule(self, selector_line: str) -> bool:
        """
        Check if a CSS rule should be kept based on its selector.
        
        Args:
            selector_line: The line containing the CSS selector
        
        Returns:
            True if the rule should be kept, False otherwise
        """
        # Extract class names from selector
        # Match .k-class-name including escaped characters
        class_pattern = r'\.([k]-[\w-]+(?:\\:[\w-]+)*)'
        matches = re.findall(class_pattern, selector_line)
        
        if not matches:
            # No KardoCSS classes found, keep it (might be base styles or @rules)
            return True
        
        # Check if any of the classes in the selector are used
        for match in matches:
            # Unescape the class name
            unescaped = match.replace('\\:', ':')
            
            if unescaped in self.used_classes:
                return True
            
            # Check for partial matches (e.g., dark:k-bg-primary matches k-bg-primary)
            for used_class in self.used_classes:
                if unescaped in used_class or used_class in unescaped:
                    return True
        
        return False
    
    def get_stats(self) -> dict:
        """
        Get statistics about the purging process.
        
        Returns:
            Dictionary with statistics
        """
        return {
            'total_classes': len(self.all_classes),
            'used_classes': len(self.used_classes),
            'unused_classes': len(self.all_classes - self.used_classes),
            'usage_percentage': (len(self.used_classes) / len(self.all_classes) * 100) if self.all_classes else 0,
        }


def purge_css(
    css_content: str,
    scan_patterns: List[str],
    base_dir: str = ".",
    safelist: Optional[List[str]] = None,
    keep_base_styles: bool = True
) -> str:
    """
    Convenience function to purge CSS in one call.
    
    Args:
        css_content: The CSS content to purge
        scan_patterns: List of glob patterns to scan for used classes
        base_dir: Base directory to scan from
        safelist: List of classes to always keep
        keep_base_styles: Whether to keep base styles
    
    Returns:
        Purged CSS content
    
    Example:
        >>> purged = purge_css(
        ...     css_content=compiled_css,
        ...     scan_patterns=['**/*.html', '**/*.jsx'],
        ...     safelist=['k-container', 'k-btn-*']
        ... )
    """
    purger = CSSPurger(css_content)
    purger.scan_files(scan_patterns, base_dir)
    
    if safelist:
        purger.add_safelist(safelist)
    
    stats = purger.get_stats()
    logger.info(f"Usage: {stats['used_classes']}/{stats['total_classes']} classes ({stats['usage_percentage']:.1f}%)")
    
    return purger.purge(keep_base_styles=keep_base_styles)

