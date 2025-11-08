#!/usr/bin/env python3
"""
Olog Tool - A command-line tool for backing up, restoring, and generating reports from Olog servers.

2025 Andrea Michelotti
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any
import requests
from requests.auth import HTTPBasicAuth
import base64

try:
    from reportlab.platypus import Flowable
except ImportError:
    Flowable = None


class OlogClient:
    """Client for interacting with Olog REST API."""
    
    def __init__(self, url: str, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize Olog client.
        
        Args:
            url: Base URL of the Olog server
            username: Optional username for authentication
            password: Optional password for authentication
        """
        self.base_url = url.rstrip('/')
        self.auth = HTTPBasicAuth(username, password) if username and password else None
        self.session = requests.Session()
        if self.auth:
            self.session.auth = self.auth
    
    def search_logs(self, start: Optional[str] = None, end: Optional[str] = None, 
                    size: int = 1000, **kwargs) -> List[Dict[str, Any]]:
        """
        Search for logs in the given time range.
        
        Args:
            start: Start time in ISO format (YYYY-MM-DDTHH:MM:SS)
            end: End time in ISO format (YYYY-MM-DDTHH:MM:SS)
            size: Maximum number of results to return
            **kwargs: Additional search parameters
            
        Returns:
            List of log entries
        """
        url = f"{self.base_url}/logs"
        params = {'size': size}
        
        if start:
            params['start'] = start
        if end:
            params['end'] = end
        
        params.update(kwargs)
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error searching logs: {e}")
            return []
    
    def get_log(self, log_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific log entry by ID.
        
        Args:
            log_id: The log entry ID
            
        Returns:
            Log entry data or None if not found
        """
        url = f"{self.base_url}/logs/{log_id}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting log {log_id}: {e}")
            return None
    
    def download_attachment(self, log_id: int, attachment_name: str, output_path: Path) -> bool:
        """
        Download an attachment from a log entry.
        
        Args:
            log_id: The log entry ID
            attachment_name: Name of the attachment
            output_path: Path to save the attachment
            
        Returns:
            True if successful, False otherwise
        """
        url = f"{self.base_url}/logs/attachments/{log_id}/{attachment_name}"
        
        try:
            response = self.session.get(url, stream=True)
            response.raise_for_status()
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error downloading attachment {attachment_name}: {e}")
            return False
    
    def create_log(self, log_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new log entry.
        
        Args:
            log_data: Log entry data
            
        Returns:
            Created log entry or None if failed
        """
        url = f"{self.base_url}/logs"
        
        try:
            response = self.session.put(url, json=log_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error creating log: {e}")
            return None
    
    def upload_attachment(self, log_id: int, file_path: Path) -> bool:
        """
        Upload an attachment to a log entry.
        
        Args:
            log_id: The log entry ID
            file_path: Path to the file to upload
            
        Returns:
            True if successful, False otherwise
        """
        url = f"{self.base_url}/logs/attachments/{log_id}"
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.name, f)}
                response = self.session.post(url, files=files)
                response.raise_for_status()
            return True
        except (requests.exceptions.RequestException, IOError) as e:
            print(f"Error uploading attachment {file_path}: {e}")
            return False


class OlogBackup:
    """Handle backup and restore operations for Olog."""
    
    def __init__(self, client: OlogClient):
        """
        Initialize backup handler.
        
        Args:
            client: OlogClient instance
        """
        self.client = client
    
    def backup(self, output_dir: Path, start: Optional[str] = None, 
               end: Optional[str] = None) -> bool:
        """
        Perform a complete backup of logs and attachments.
        
        Args:
            output_dir: Directory to store backup
            start: Start time for backup
            end: End time for backup
            
        Returns:
            True if successful, False otherwise
        """
        print(f"Starting backup to {output_dir}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Search for logs
        logs = self.client.search_logs(start=start, end=end, size=10000)
        
        if not logs:
            print("No logs found in the specified time range")
            return False
        
        print(f"Found {len(logs)} logs")
        
        # Save logs metadata
        logs_file = output_dir / 'logs.json'
        with open(logs_file, 'w') as f:
            json.dump(logs, f, indent=2)
        
        print(f"Saved logs metadata to {logs_file}")
        
        # Download attachments
        attachments_dir = output_dir / 'attachments'
        attachments_dir.mkdir(exist_ok=True)
        
        for log in logs:
            log_id = log.get('id')
            attachments = log.get('attachments', [])
            
            if attachments:
                log_attachments_dir = attachments_dir / str(log_id)
                log_attachments_dir.mkdir(exist_ok=True)
                
                for attachment in attachments:
                    att_name = attachment.get('filename') or attachment.get('name')
                    if att_name:
                        output_path = log_attachments_dir / att_name
                        print(f"Downloading attachment: {att_name} for log {log_id}")
                        self.client.download_attachment(log_id, att_name, output_path)
        
        print("Backup completed successfully")
        return True
    
    def restore(self, backup_dir: Path) -> bool:
        """
        Restore logs and attachments from a backup.
        
        Args:
            backup_dir: Directory containing the backup
            
        Returns:
            True if successful, False otherwise
        """
        print(f"Starting restore from {backup_dir}")
        
        logs_file = backup_dir / 'logs.json'
        if not logs_file.exists():
            print(f"Error: logs.json not found in {backup_dir}")
            return False
        
        # Load logs metadata
        with open(logs_file, 'r') as f:
            logs = json.load(f)
        
        print(f"Found {len(logs)} logs to restore")
        
        attachments_dir = backup_dir / 'attachments'
        
        for log in logs:
            # Remove read-only fields
            log_data = {k: v for k, v in log.items() 
                       if k not in ['id', 'createdDate', 'modifyDate']}
            
            # Create log entry
            print(f"Restoring log: {log.get('title', 'Untitled')}")
            created_log = self.client.create_log(log_data)
            
            if created_log:
                new_log_id = created_log.get('id')
                old_log_id = log.get('id')
                
                # Upload attachments if they exist
                if old_log_id and attachments_dir.exists():
                    log_attachments_dir = attachments_dir / str(old_log_id)
                    if log_attachments_dir.exists():
                        for attachment_file in log_attachments_dir.iterdir():
                            print(f"Uploading attachment: {attachment_file.name}")
                            self.client.upload_attachment(new_log_id, attachment_file)
        
        print("Restore completed successfully")
        return True


class OlogReportGenerator:
    """Generate reports from Olog logs."""
    
    def __init__(self, client: OlogClient):
        """
        Initialize report generator.
        
        Args:
            client: OlogClient instance
        """
        self.client = client
    
    def _format_timestamp(self, timestamp) -> str:
        """Convert timestamp to human-readable date format."""
        if not timestamp:
            return ''
        try:
            from datetime import datetime
            dt = datetime.fromtimestamp(timestamp / 1000)  # Convert ms to seconds
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return str(timestamp)
    
    def generate_markdown(self, output_file: Path, start: Optional[str] = None,
                         end: Optional[str] = None, title: Optional[str] = None, 
                         daybreak: bool = False) -> bool:
        """
        Generate a Markdown report.
        
        Args:
            output_file: Path to output Markdown file
            start: Start time for report
            end: End time for report
            
        Returns:
            True if successful, False otherwise
        """
        print(f"Generating Markdown report to {output_file}")
        
        logs = self.client.search_logs(start=start, end=end, size=10000)
        
        if not logs:
            print("No logs found in the specified time range")
            return False
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Calculate actual time range if not specified
        if start is None and end is None:
            created_dates = [log.get('createdDate') for log in logs if log.get('createdDate')]
            if created_dates:
                # Convert timestamps to datetime objects for comparison
                from datetime import datetime
                datetime_objects = []
                for ts in created_dates:
                    try:
                        dt = datetime.fromtimestamp(ts / 1000)  # Convert ms to seconds
                        datetime_objects.append(dt)
                    except:
                        pass
                
                if datetime_objects:
                    min_dt = min(datetime_objects)
                    max_dt = max(datetime_objects)
                    start = min_dt.strftime('%Y-%m-%d %H:%M:%S')
                    end = max_dt.strftime('%Y-%m-%d %H:%M:%S')
        
        with open(output_file, 'w') as f:
            # Write header
            if title:
                f.write(f"# {title}\n\n")
            else:
                f.write("# Olog Report\n\n")
            
            # Always show time range info
            time_range_text = f"**Time Range:** {start or 'Beginning'} to {end or 'Now'}"
            f.write(f"{time_range_text}\n\n")
            
            f.write(f"**Total Logs:** {len(logs)}\n\n")
            
            # Generate Table of Contents
            f.write("## Table of Contents\n\n")
            toc_entries = []
            for i, log in enumerate(logs, 1):
                log_title = log.get('title', 'Untitled')
                # Clean title for anchor link (remove special chars, replace spaces with hyphens)
                anchor = f"log-{i}"
                toc_entries.append(f"- [{log_title}](#{anchor})")
            
            f.write("\n".join(toc_entries))
            f.write("\n\n---\n\n")
            
            # Write logs
            current_date = None
            for i, log in enumerate(logs, 1):
                title = log.get('title', 'Untitled')
                owner = log.get('owner', 'Unknown')
                created = self._format_timestamp(log.get('createdDate', ''))
                description = log.get('description', '')
                level = log.get('level', '')
                
                # Add daybreak if enabled
                if daybreak and created:
                    try:
                        from datetime import datetime
                        log_date = datetime.strptime(created, '%Y-%m-%d %H:%M:%S').date()
                        if current_date != log_date:
                            if current_date is not None:  # Not the first date
                                f.write("\n---\n\n")
                            current_date = log_date
                            day_name = log_date.strftime('%A')
                            f.write(f"# {log_date.strftime('%Y-%m-%d')} {day_name}\n\n")
                            f.write("---\n\n")
                    except:
                        pass
                
                # Add anchor for TOC link
                anchor = f"log-{i}"
                f.write(f'<a id="{anchor}"></a>\n')
                f.write(f"## {title}\n\n")
                f.write(f"**Author:** {owner}  \n")
                f.write(f"**Date:** {created}  \n")
                if level:
                    f.write(f"**Level:** {level}  \n")
                f.write(f"\n{description}\n\n")
                
                # Add tags
                tags = log.get('tags', [])
                if tags:
                    tag_names = [tag.get('name') for tag in tags if tag.get('name')]
                    if tag_names:
                        f.write(f"**Tags:** {', '.join(tag_names)}\n\n")
                
                # Add logbooks
                logbooks = log.get('logbooks', [])
                if logbooks:
                    logbook_names = [lb.get('name') for lb in logbooks if lb.get('name')]
                    if logbook_names:
                        f.write(f"**Logbooks:** {', '.join(logbook_names)}\n\n")
                
                # Add properties
                properties = log.get('properties', [])
                if properties:
                    f.write("**Properties:**\n\n")
                    for prop in properties:
                        prop_name = prop.get('name', '')
                        attributes = prop.get('attributes', [])
                        if attributes:
                            f.write(f"- {prop_name}:\n")
                            for attr in attributes:
                                attr_name = attr.get('name', '')
                                attr_value = attr.get('value', '')
                                f.write(f"  - {attr_name}: {attr_value}\n")
                        else:
                            f.write(f"- {prop_name}\n")
                    f.write("\n")
                
                # List attachments
                attachments = log.get('attachments', [])
                if attachments:
                    f.write("**Attachments:**\n\n")
                    for att in attachments:
                        att_name = att.get('filename') or att.get('name', 'Unknown')
                        f.write(f"- {att_name}\n")
                    f.write("\n")
                
                f.write("---\n\n")
        
        print(f"Markdown report generated successfully")
        return True

    class BookmarkFlowable(Flowable):
        """A custom flowable that adds a PDF bookmark at its position."""
        
        def __init__(self, name):
            Flowable.__init__(self)
            self.name = name
        
        def draw(self):
            # Add a bookmark at this position
            self.canv.bookmarkPage(self.name)
            # Make it visible in the outline
            self.canv.addOutlineEntry(self.name, self.name, 0)

    def generate_pdf(self, output_file: Path, start: Optional[str] = None,
                    end: Optional[str] = None, embed_attachments: bool = True, 
                    title: Optional[str] = None, daybreak: bool = False) -> bool:
        """
        Generate a PDF report with embedded attachments.
        
        Args:
            output_file: Path to output PDF file
            start: Start time for report
            end: End time for report
            embed_attachments: Whether to embed images in the PDF
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Flowable
            from reportlab.lib.enums import TA_LEFT, TA_CENTER
            from reportlab.lib.utils import ImageReader
            from io import BytesIO
        except ImportError as e:
            print(f"Error importing reportlab: {e}")
            print("Error: reportlab is required for PDF generation")
            print("Install it with: pip install reportlab")
            return False
        
        print(f"Generating PDF report to {output_file}")
        
        logs = self.client.search_logs(start=start, end=end, size=10000)
        
        if not logs:
            print("No logs found in the specified time range")
            return False
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Calculate actual time range if not specified
        if start is None and end is None:
            created_dates = [log.get('createdDate') for log in logs if log.get('createdDate')]
            if created_dates:
                # Convert timestamps to datetime objects for comparison
                from datetime import datetime
                datetime_objects = []
                for ts in created_dates:
                    try:
                        dt = datetime.fromtimestamp(ts / 1000)  # Convert ms to seconds
                        datetime_objects.append(dt)
                    except:
                        pass
                
                if datetime_objects:
                    min_dt = min(datetime_objects)
                    max_dt = max(datetime_objects)
                    start = min_dt.strftime('%Y-%m-%d %H:%M:%S')
                    end = max_dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Create PDF
        doc = SimpleDocTemplate(str(output_file), pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor='#000000',
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        date_break_style = ParagraphStyle(
            'DateBreak',
            parent=styles['Heading1'],
            fontSize=36,
            textColor='#2c3e50',
            spaceAfter=20,
            spaceBefore=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor='#000000',
            spaceAfter=12
        )
        
        # Title
        report_title = title or "Olog Report"
        story.append(Paragraph(report_title, title_style))
        story.append(Spacer(1, 0.2 * inch))
        
        # Time range (always show)
        time_range = f"Time Range: {start or 'Beginning'} to {end or 'Now'}"
        story.append(Paragraph(time_range, styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))
        
        # Total count
        story.append(Paragraph(f"Total Logs: {len(logs)}", styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))
        
        # Add TOC
        story.append(Paragraph("Table of Contents", styles['Heading2']))
        story.append(Spacer(1, 0.1 * inch))
        
        # Add TOC entries with links
        for i, log in enumerate(logs, 1):
            log_title = log.get('title', 'Untitled')
            bookmark_name = f"log-{i}"
            # Create a paragraph with a link to the bookmark
            toc_entry = Paragraph(f'<a href="#{bookmark_name}">{i}. {log_title}</a>', styles['Normal'])
            story.append(toc_entry)
            story.append(Spacer(1, 0.05 * inch))
        
        story.append(PageBreak())
        
        # Page break to start logs on next page
        story.append(PageBreak())
        
        # Add logs
        current_date = None
        for i, log in enumerate(logs):
            title = log.get('title', 'Untitled')
            owner = log.get('owner', 'Unknown')
            created = self._format_timestamp(log.get('createdDate', ''))
            description = log.get('description', '').replace('<', '&lt;').replace('>', '&gt;')
            level = log.get('level', '')
            
            # Add daybreak if enabled
            if daybreak and created:
                try:
                    from datetime import datetime
                    log_date = datetime.strptime(created, '%Y-%m-%d %H:%M:%S').date()
                    if current_date != log_date:
                        current_date = log_date
                        day_name = log_date.strftime('%A')
                        story.append(Paragraph(f"{log_date.strftime('%Y-%m-%d')} {day_name}", date_break_style))
                        story.append(Spacer(1, 0.5 * inch))
                except:
                    pass
            
            # Log title
            bookmark_name = f"log-{i+1}"
            story.append(self.BookmarkFlowable(bookmark_name))
            story.append(Paragraph(title, heading_style))
            
            # Metadata
            story.append(Paragraph(f"<b>Author:</b> {owner}", styles['Normal']))
            story.append(Paragraph(f"<b>Date:</b> {created}", styles['Normal']))
            if level:
                story.append(Paragraph(f"<b>Level:</b> {level}", styles['Normal']))
            story.append(Spacer(1, 0.1 * inch))
            
            # Description
            story.append(Paragraph(description, styles['Normal']))
            story.append(Spacer(1, 0.1 * inch))
            
            # Tags
            tags = log.get('tags', [])
            if tags:
                tag_names = [tag.get('name') for tag in tags if tag.get('name')]
                if tag_names:
                    story.append(Paragraph(f"<b>Tags:</b> {', '.join(tag_names)}", styles['Normal']))
            
            # Logbooks
            logbooks = log.get('logbooks', [])
            if logbooks:
                logbook_names = [lb.get('name') for lb in logbooks if lb.get('name')]
                if logbook_names:
                    story.append(Paragraph(f"<b>Logbooks:</b> {', '.join(logbook_names)}", styles['Normal']))
            
            # Attachments
            attachments = log.get('attachments', [])
            if attachments:
                story.append(Spacer(1, 0.1 * inch))
                story.append(Paragraph("<b>Attachments:</b>", styles['Normal']))
                story.append(Spacer(1, 0.05 * inch))
                
                for att in attachments:
                    att_name = att.get('filename') or att.get('name', 'Unknown')
                    story.append(Paragraph(f"• {att_name}", styles['Normal']))
                    
                    # Try to embed image attachments
                    if embed_attachments and log.get('id'):
                        log_id = log.get('id')
                        # Check if it's an image file
                        if att_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                            try:
                                # Download attachment
                                url = f"{self.client.base_url}/logs/attachments/{log_id}/{att_name}"
                                response = self.client.session.get(url)
                                response.raise_for_status()
                                
                                # Create image from bytes
                                img_data = BytesIO(response.content)
                                img = Image(img_data)
                                
                                # Scale image to fit page width (with margins)
                                max_width = 6 * inch
                                max_height = 4 * inch
                                
                                img_width, img_height = img.imageWidth, img.imageHeight
                                aspect = img_height / float(img_width)
                                
                                if img_width > max_width:
                                    img_width = max_width
                                    img_height = img_width * aspect
                                
                                if img_height > max_height:
                                    img_height = max_height
                                    img_width = img_height / aspect
                                
                                img.drawWidth = img_width
                                img.drawHeight = img_height
                                
                                story.append(Spacer(1, 0.1 * inch))
                                story.append(img)
                                story.append(Spacer(1, 0.1 * inch))
                            except Exception as e:
                                print(f"Warning: Could not embed image {att_name}: {e}")
            
            # Add page break between logs (except for the last one)
            if i < len(logs) - 1:
                story.append(PageBreak())
        
        # Build PDF
        doc.build(story)
        
        print(f"PDF report generated successfully")
        return True
    
    def generate_html(self, output_file: Path, start: Optional[str] = None,
                     end: Optional[str] = None, embed_attachments: bool = True,
                     title: Optional[str] = None, daybreak: bool = False) -> bool:
        """
        Generate an HTML report with embedded attachments.
        
        Args:
            output_file: Path to output HTML file
            start: Start time for report
            end: End time for report
            embed_attachments: Whether to embed images as base64 in the HTML
            
        Returns:
            True if successful, False otherwise
        """
        print(f"Generating HTML report to {output_file}")
        
        logs = self.client.search_logs(start=start, end=end, size=10000)
        
        if not logs:
            print("No logs found in the specified time range")
            return False
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Calculate actual time range if not specified
        if start is None and end is None:
            created_dates = [log.get('createdDate') for log in logs if log.get('createdDate')]
            if created_dates:
                # Convert timestamps to datetime objects for comparison
                from datetime import datetime
                datetime_objects = []
                for ts in created_dates:
                    try:
                        dt = datetime.fromtimestamp(ts / 1000)  # Convert ms to seconds
                        datetime_objects.append(dt)
                    except:
                        pass
                
                if datetime_objects:
                    min_dt = min(datetime_objects)
                    max_dt = max(datetime_objects)
                    start = min_dt.strftime('%Y-%m-%d %H:%M:%S')
                    end = max_dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # HTML template
        report_title = title or "Olog Report"
        
        html_content = ""
        
        css_styles = """
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background-color: #2c3e50;
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 5px;
            margin-bottom: 30px;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
        }
        .header .info {
            margin-top: 15px;
            font-size: 1.1em;
        }
        .log-entry {
            background-color: white;
            padding: 25px;
            margin-bottom: 25px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .log-entry.first-log {
            page-break-before: always;
        }
        .date-break {
            background-color: #34495e;
            color: white;
            padding: 40px;
            text-align: center;
            margin: 30px 0;
            border-radius: 10px;
            font-size: 48px;
            font-weight: bold;
            page-break-before: always;
        }
        .log-entry h2 {
            color: #2c3e50;
            margin-top: 0;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        .metadata {
            display: grid;
            grid-template-columns: auto 1fr;
            gap: 10px;
            margin: 15px 0;
            font-size: 0.95em;
        }
        .metadata .label {
            font-weight: bold;
            color: #555;
        }
        .metadata .value {
            color: #333;
        }
        .description {
            margin: 20px 0;
            line-height: 1.6;
            white-space: pre-wrap;
            background-color: #f9f9f9;
            padding: 15px;
            border-left: 4px solid #3498db;
            border-radius: 3px;
        }
        .tags, .logbooks {
            margin: 15px 0;
        }
        .tag, .logbook {
            display: inline-block;
            background-color: #3498db;
            color: white;
            padding: 5px 12px;
            margin: 3px;
            border-radius: 15px;
            font-size: 0.9em;
        }
        .logbook {
            background-color: #e74c3c;
        }
        .properties {
            margin: 15px 0;
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 3px;
        }
        .properties h4 {
            margin-top: 0;
            color: #555;
        }
        .property {
            margin: 10px 0;
        }
        .property-name {
            font-weight: bold;
            color: #2c3e50;
        }
        .property-attr {
            margin-left: 20px;
            color: #555;
        }
        .attachments {
            margin: 20px 0;
        }
        .attachments h4 {
            color: #555;
        }
        .attachment-item {
            margin: 10px 0;
            padding: 10px;
            background-color: #f9f9f9;
            border-radius: 3px;
        }
        .attachment-name {
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .attachment-image {
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 3px;
            margin-top: 10px;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #777;
            font-size: 0.9em;
        }
        .toc {
            background-color: white;
            padding: 25px;
            margin-bottom: 30px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .toc h2 {
            color: #2c3e50;
            margin-top: 0;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        .toc ul {
            list-style-type: none;
            padding: 0;
        }
        .toc li {
            margin: 8px 0;
        }
        .toc a {
            color: #3498db;
            text-decoration: none;
            font-weight: 500;
        }
        .toc a:hover {
            text-decoration: underline;
        }
        """
        
        html_content += f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report_title}</title>
    <style>{css_styles}</style>
</head>
<body>
    <div class="header">
        <h1>{report_title}</h1>
        <div class="info">"""
        
        # Always add time range info
        time_range_info = f"Time Range: {start or 'Beginning'} to {end or 'Now'}"
        html_content += f"            <div>{time_range_info}</div>\n"
        
        html_content += f"            <div>Total Logs: {len(logs)}</div>\n"
        html_content += "        </div>\n    </div>\n\n"
        
        # Generate Table of Contents
        html_content += '    <div class="toc">\n'
        html_content += '        <h2>Table of Contents</h2>\n'
        html_content += '        <ul>\n'
        for i, log in enumerate(logs, 1):
            log_title = log.get('title', 'Untitled')
            anchor = f"log-{i}"
            html_content += f'            <li><a href="#{anchor}">{log_title}</a></li>\n'
        html_content += '        </ul>\n'
        html_content += '    </div>\n\n'
        
        # Add logs
        current_date = None
        for i, log in enumerate(logs):
            log_id = log.get('id')
            title = log.get('title', 'Untitled')
            owner = log.get('owner', 'Unknown')
            created = self._format_timestamp(log.get('createdDate', ''))
            description = log.get('description', '').replace('<', '&lt;').replace('>', '&gt;')
            level = log.get('level', '')
            
            # Add daybreak if enabled
            if daybreak and created:
                try:
                    from datetime import datetime
                    log_date = datetime.strptime(created, '%Y-%m-%d %H:%M:%S').date()
                    if current_date != log_date:
                        current_date = log_date
                        day_name = log_date.strftime('%A')
                        html_content += '    <div class="date-break">\n'
                        html_content += f'        {log_date.strftime("%Y-%m-%d")} {day_name}\n'
                        html_content += '    </div>\n\n'
                except:
                    pass
            
            # Add first-log class to the first log entry
            log_class = 'log-entry first-log' if i == 0 else 'log-entry'
            anchor = f"log-{i+1}"
            html_content += f'    <div id="{anchor}" class="{log_class}">\n'
            html_content += f'        <h2>{title}</h2>\n'
            html_content += '        <div class="metadata">\n'
            html_content += f'            <div class="label">Author:</div><div class="value">{owner}</div>\n'
            html_content += f'            <div class="label">Date:</div><div class="value">{created}</div>\n'
            if level:
                html_content += f'            <div class="label">Level:</div><div class="value">{level}</div>\n'
            if log_id:
                html_content += f'            <div class="label">Log ID:</div><div class="value">{log_id}</div>\n'
            html_content += '        </div>\n'
            
            # Description
            if description:
                html_content += f'        <div class="description">{description}</div>\n'
            
            # Tags
            tags = log.get('tags', [])
            if tags:
                tag_names = [tag.get('name') for tag in tags if tag.get('name')]
                if tag_names:
                    html_content += '        <div class="tags">\n'
                    html_content += '            <strong>Tags:</strong> '
                    for tag in tag_names:
                        html_content += f'<span class="tag">{tag}</span> '
                    html_content += '\n        </div>\n'
            
            # Logbooks
            logbooks = log.get('logbooks', [])
            if logbooks:
                logbook_names = [lb.get('name') for lb in logbooks if lb.get('name')]
                if logbook_names:
                    html_content += '        <div class="logbooks">\n'
                    html_content += '            <strong>Logbooks:</strong> '
                    for lb in logbook_names:
                        html_content += f'<span class="logbook">{lb}</span> '
                    html_content += '\n        </div>\n'
            
            # Properties
            properties = log.get('properties', [])
            if properties:
                html_content += '        <div class="properties">\n'
                html_content += '            <h4>Properties</h4>\n'
                for prop in properties:
                    prop_name = prop.get('name', '')
                    html_content += f'            <div class="property">\n'
                    html_content += f'                <div class="property-name">{prop_name}</div>\n'
                    attributes = prop.get('attributes', [])
                    if attributes:
                        for attr in attributes:
                            attr_name = attr.get('name', '')
                            attr_value = attr.get('value', '')
                            html_content += f'                <div class="property-attr">{attr_name}: {attr_value}</div>\n'
                    html_content += '            </div>\n'
                html_content += '        </div>\n'
            
            # Attachments
            attachments = log.get('attachments', [])
            if attachments:
                html_content += '        <div class="attachments">\n'
                html_content += '            <h4>Attachments</h4>\n'
                
                for att in attachments:
                    att_name = att.get('filename') or att.get('name', 'Unknown')
                    html_content += '            <div class="attachment-item">\n'
                    html_content += f'                <div class="attachment-name">{att_name}</div>\n'
                    
                    # Try to embed image attachments as base64
                    if embed_attachments and log_id:
                        if att_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg')):
                            try:
                                url = f"{self.client.base_url}/logs/attachments/{log_id}/{att_name}"
                                response = self.client.session.get(url)
                                response.raise_for_status()
                                
                                # Convert to base64
                                import base64
                                img_base64 = base64.b64encode(response.content).decode('utf-8')
                                
                                # Determine MIME type
                                ext = att_name.lower().split('.')[-1]
                                mime_types = {
                                    'png': 'image/png',
                                    'jpg': 'image/jpeg',
                                    'jpeg': 'image/jpeg',
                                    'gif': 'image/gif',
                                    'bmp': 'image/bmp',
                                    'svg': 'image/svg+xml'
                                }
                                mime_type = mime_types.get(ext, 'image/png')
                                
                                html_content += f'                <img src="data:{mime_type};base64,{img_base64}" class="attachment-image" alt="{att_name}" />\n'
                            except Exception as e:
                                print(f"Warning: Could not embed image {att_name}: {e}")
                                html_content += f'                <div style="color: #999; font-style: italic;">Image could not be embedded</div>\n'
                    
                    html_content += '            </div>\n'
                html_content += '        </div>\n'
            
            html_content += '    </div>\n\n'
        
        # Footer
        html_content += '    <div class="footer">\n'
        html_content += f'        Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
        html_content += '    </div>\n'
        html_content += '</body>\n</html>'
        
        # Write HTML file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTML report generated successfully")
        return True


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description='Olog Tool - Backup, restore, and generate reports from Olog servers',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--url', required=True, help='Olog server URL')
    parser.add_argument('--username', '-u', help='Username for authentication')
    parser.add_argument('--password', '-p', help='Password for authentication')
    parser.add_argument('--start', help='Start time (ISO format: YYYY-MM-DDTHH:MM:SS)')
    parser.add_argument('--end', help='End time (ISO format: YYYY-MM-DDTHH:MM:SS)')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Backup logs and attachments')
    backup_parser.add_argument('--output', '-o', required=True, help='Output directory for backup')
    
    # Restore command
    restore_parser = subparsers.add_parser('restore', help='Restore logs and attachments from backup')
    restore_parser.add_argument('--input', '-i', required=True, help='Input directory containing backup')
    
    # Report commands
    markdown_parser = subparsers.add_parser('markdown', help='Generate Markdown report')
    markdown_parser.add_argument('--output', '-o', required=True, help='Output Markdown file')
    markdown_parser.add_argument('--title', help='Report title')
    markdown_parser.add_argument('--daybreak', action='store_true', help='Add date separators between different days')
    
    pdf_parser = subparsers.add_parser('pdf', help='Generate PDF report')
    pdf_parser.add_argument('--output', '-o', required=True, help='Output PDF file')
    pdf_parser.add_argument('--no-embed', action='store_true', help='Do not embed attachments in PDF')
    pdf_parser.add_argument('--title', help='Report title')
    pdf_parser.add_argument('--daybreak', action='store_true', help='Add date separators between different days')
    
    html_parser = subparsers.add_parser('html', help='Generate HTML report')
    html_parser.add_argument('--output', '-o', required=True, help='Output HTML file')
    html_parser.add_argument('--no-embed', action='store_true', help='Do not embed attachments in HTML')
    html_parser.add_argument('--title', help='Report title')
    html_parser.add_argument('--daybreak', action='store_true', help='Add date separators between different days')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Create client
    client = OlogClient(args.url, args.username, args.password)
    
    # Execute command
    if args.command == 'backup':
        backup = OlogBackup(client)
        success = backup.backup(Path(args.output), args.start, args.end)
        return 0 if success else 1
    
    elif args.command == 'restore':
        backup = OlogBackup(client)
        success = backup.restore(Path(args.input))
        return 0 if success else 1
    
    elif args.command == 'markdown':
        generator = OlogReportGenerator(client)
        success = generator.generate_markdown(Path(args.output), args.start, args.end, args.title, args.daybreak)
        return 0 if success else 1
    
    elif args.command == 'pdf':
        generator = OlogReportGenerator(client)
        embed = not args.no_embed
        success = generator.generate_pdf(Path(args.output), args.start, args.end, embed, args.title, args.daybreak)
        return 0 if success else 1
    
    elif args.command == 'html':
        generator = OlogReportGenerator(client)
        embed = not args.no_embed
        success = generator.generate_html(Path(args.output), args.start, args.end, embed, args.title, args.daybreak)
        return 0 if success else 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
