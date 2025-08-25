"""
Contact Synchronization Module
Handles contact management and synchronization between mobile device and PC.
"""

import json
import csv
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import re

class Contact:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.first_name = kwargs.get('first_name', '')
        self.last_name = kwargs.get('last_name', '')
        self.company = kwargs.get('company', '')
        self.job_title = kwargs.get('job_title', '')
        self.emails = kwargs.get('emails', [])
        self.phones = kwargs.get('phones', [])
        self.addresses = kwargs.get('addresses', [])
        self.birthday = kwargs.get('birthday')
        self.notes = kwargs.get('notes', '')
        self.created = kwargs.get('created', datetime.now())
        self.modified = kwargs.get('modified', datetime.now())
        self.source = kwargs.get('source', 'unknown')  # 'device', 'pc', 'cloud'
        
    def to_dict(self) -> Dict:
        """Convert contact to dictionary"""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'company': self.company,
            'job_title': self.job_title,
            'emails': self.emails,
            'phones': self.phones,
            'addresses': self.addresses,
            'birthday': self.birthday.isoformat() if self.birthday else None,
            'notes': self.notes,
            'created': self.created.isoformat(),
            'modified': self.modified.isoformat(),
            'source': self.source
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'Contact':
        """Create contact from dictionary"""
        if 'birthday' in data and data['birthday']:
            try:
                data['birthday'] = datetime.fromisoformat(data['birthday'])
            except ValueError:
                data['birthday'] = None
                
        if 'created' in data and data['created']:
            try:
                data['created'] = datetime.fromisoformat(data['created'])
            except ValueError:
                data['created'] = datetime.now()
                
        if 'modified' in data and data['modified']:
            try:
                data['modified'] = datetime.fromisoformat(data['modified'])
            except ValueError:
                data['modified'] = datetime.now()
                
        return cls(**data)
        
    def get_full_name(self) -> str:
        """Get full name of contact"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return "Unknown"
            
    def get_primary_phone(self) -> Optional[str]:
        """Get primary phone number"""
        return self.phones[0] if self.phones else None
        
    def get_primary_email(self) -> Optional[str]:
        """Get primary email address"""
        return self.emails[0] if self.emails else None
        
    def is_duplicate_of(self, other: 'Contact') -> bool:
        """Check if this contact is a duplicate of another"""
        # Check by name and phone/email
        if self.get_full_name() == other.get_full_name():
            if self.get_primary_phone() and other.get_primary_phone():
                if self.get_primary_phone() == other.get_primary_phone():
                    return True
            if self.get_primary_email() and other.get_primary_email():
                if self.get_primary_email() == other.get_primary_email():
                    return True
        return False

class ContactSyncModule:
    def __init__(self):
        self.contacts: List[Contact] = []
        self.sync_config = {
            'merge_duplicates': True,
            'sync_deleted': True,
            'backup_before_sync': True,
            'validate_emails': True,
            'validate_phones': True,
            'sync_frequency': 'manual'  # 'manual', 'hourly', 'daily'
        }
        
        self.sync_history = []
        self.duplicate_contacts = []
        
    def add_contact(self, contact: Contact) -> bool:
        """Add a new contact"""
        try:
            # Validate contact data
            if not self._validate_contact(contact):
                return False
                
            # Check for duplicates
            if self.sync_config['merge_duplicates']:
                duplicate = self._find_duplicate(contact)
                if duplicate:
                    self._merge_contacts(duplicate, contact)
                    return True
                    
            # Generate ID if not provided
            if not contact.id:
                contact.id = self._generate_contact_id()
                
            contact.created = datetime.now()
            contact.modified = datetime.now()
            
            self.contacts.append(contact)
            return True
            
        except Exception as e:
            print(f"Error adding contact: {e}")
            return False
            
    def update_contact(self, contact_id: str, updates: Dict) -> bool:
        """Update an existing contact"""
        try:
            contact = self._find_contact_by_id(contact_id)
            if not contact:
                return False
                
            # Update fields
            for key, value in updates.items():
                if hasattr(contact, key):
                    setattr(contact, key, value)
                    
            contact.modified = datetime.now()
            return True
            
        except Exception as e:
            print(f"Error updating contact: {e}")
            return False
            
    def delete_contact(self, contact_id: str) -> bool:
        """Delete a contact"""
        try:
            contact = self._find_contact_by_id(contact_id)
            if contact:
                self.contacts.remove(contact)
                return True
            return False
            
        except Exception as e:
            print(f"Error deleting contact: {e}")
            return False
            
    def _validate_contact(self, contact: Contact) -> bool:
        """Validate contact data"""
        # Check required fields
        if not contact.first_name and not contact.last_name:
            print("Contact must have at least a first or last name")
            return False
            
        # Validate emails
        if self.sync_config['validate_emails']:
            for email in contact.emails:
                if not self._is_valid_email(email):
                    print(f"Invalid email format: {email}")
                    return False
                    
        # Validate phone numbers
        if self.sync_config['validate_phones']:
            for phone in contact.phones:
                if not self._is_valid_phone(phone):
                    print(f"Invalid phone format: {phone}")
                    return False
                    
        return True
        
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
        
    def _is_valid_phone(self, phone: str) -> bool:
        """Validate phone number format"""
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        return len(digits_only) >= 10
        
    def _find_duplicate(self, contact: Contact) -> Optional[Contact]:
        """Find duplicate contact"""
        for existing in self.contacts:
            if contact.is_duplicate_of(existing):
                return existing
        return None
        
    def _merge_contacts(self, existing: Contact, new: Contact):
        """Merge two contacts"""
        # Merge fields, preferring newer data
        if new.modified > existing.modified:
            # New contact is newer, update existing
            existing.first_name = new.first_name or existing.first_name
            existing.last_name = new.last_name or existing.last_name
            existing.company = new.company or existing.company
            existing.job_title = new.job_title or existing.job_title
            
            # Merge lists
            existing.emails = list(set(existing.emails + new.emails))
            existing.phones = list(set(existing.phones + new.phones))
            existing.addresses = list(set(existing.addresses + new.addresses))
            
            existing.notes = new.notes or existing.notes
            existing.modified = datetime.now()
            
        # Add to duplicate list for review
        self.duplicate_contacts.append({
            'existing': existing,
            'new': new,
            'merged': True,
            'timestamp': datetime.now()
        })
        
    def _generate_contact_id(self) -> str:
        """Generate unique contact ID"""
        import uuid
        return str(uuid.uuid4())
        
    def _find_contact_by_id(self, contact_id: str) -> Optional[Contact]:
        """Find contact by ID"""
        for contact in self.contacts:
            if contact.id == contact_id:
                return contact
        return None
        
    def search_contacts(self, query: str) -> List[Contact]:
        """Search contacts by name, company, or phone"""
        query = query.lower()
        results = []
        
        for contact in self.contacts:
            if (query in contact.first_name.lower() or
                query in contact.last_name.lower() or
                query in contact.company.lower() or
                any(query in phone.lower() for phone in contact.phones) or
                any(query in email.lower() for email in contact.emails)):
                results.append(contact)
                
        return results
        
    def import_contacts_csv(self, file_path: str, source: str = 'pc') -> Dict:
        """Import contacts from CSV file"""
        import_results = {
            'imported': 0,
            'skipped': 0,
            'errors': 0,
            'errors_list': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row_num, row in enumerate(reader, 1):
                    try:
                        # Map CSV columns to contact fields
                        contact_data = {
                            'first_name': row.get('First Name', ''),
                            'last_name': row.get('Last Name', ''),
                            'company': row.get('Company', ''),
                            'job_title': row.get('Job Title', ''),
                            'emails': [row.get('Email', '')] if row.get('Email') else [],
                            'phones': [row.get('Phone', '')] if row.get('Phone') else [],
                            'addresses': [row.get('Address', '')] if row.get('Address') else [],
                            'notes': row.get('Notes', ''),
                            'source': source
                        }
                        
                        # Clean up empty values
                        contact_data = {k: v for k, v in contact_data.items() if v}
                        
                        contact = Contact(**contact_data)
                        
                        if self.add_contact(contact):
                            import_results['imported'] += 1
                        else:
                            import_results['skipped'] += 1
                            
                    except Exception as e:
                        import_results['errors'] += 1
                        import_results['errors_list'].append(f"Row {row_num}: {str(e)}")
                        
        except Exception as e:
            import_results['errors'] += 1
            import_results['errors_list'].append(f"File error: {str(e)}")
            
        return import_results
        
    def export_contacts_csv(self, file_path: str) -> bool:
        """Export contacts to CSV file"""
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['First Name', 'Last Name', 'Company', 'Job Title', 
                            'Email', 'Phone', 'Address', 'Notes', 'Created', 'Modified']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                writer.writeheader()
                
                for contact in self.contacts:
                    writer.writerow({
                        'First Name': contact.first_name,
                        'Last Name': contact.last_name,
                        'Company': contact.company,
                        'Job Title': contact.job_title,
                        'Email': contact.get_primary_email() or '',
                        'Phone': contact.get_primary_phone() or '',
                        'Address': contact.addresses[0] if contact.addresses else '',
                        'Notes': contact.notes,
                        'Created': contact.created.strftime('%Y-%m-%d %H:%M:%S'),
                        'Modified': contact.modified.strftime('%Y-%m-%d %H:%M:%S')
                    })
                    
            return True
            
        except Exception as e:
            print(f"Error exporting contacts: {e}")
            return False
            
    def sync_with_device(self, device_contacts: List[Contact]) -> Dict:
        """Synchronize contacts with device"""
        sync_results = {
            'added': 0,
            'updated': 0,
            'deleted': 0,
            'conflicts': 0,
            'start_time': datetime.now(),
            'end_time': None
        }
        
        try:
            # Create backup if configured
            if self.sync_config['backup_before_sync']:
                self._create_backup()
                
            # Find new contacts on device
            for device_contact in device_contacts:
                if not self._find_duplicate(device_contact):
                    device_contact.source = 'device'
                    if self.add_contact(device_contact):
                        sync_results['added'] += 1
                        
            # Find contacts deleted on device
            if self.sync_config['sync_deleted']:
                device_contact_ids = {c.id for c in device_contacts if c.id}
                for contact in self.contacts[:]:  # Copy list to avoid modification during iteration
                    if contact.source == 'device' and contact.id not in device_contact_ids:
                        self.contacts.remove(contact)
                        sync_results['deleted'] += 1
                        
        except Exception as e:
            print(f"Error during contact sync: {e}")
            
        sync_results['end_time'] = datetime.now()
        sync_results['duration'] = sync_results['end_time'] - sync_results['start_time']
        
        # Add to sync history
        self.sync_history.append(sync_results)
        
        return sync_results
        
    def _create_backup(self):
        """Create backup of current contacts"""
        backup_file = f"contacts_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            contacts_data = [contact.to_dict() for contact in self.contacts]
            with open(backup_file, 'w') as f:
                json.dump(contacts_data, f, indent=2)
        except Exception as e:
            print(f"Error creating backup: {e}")
            
    def get_contacts_summary(self) -> Dict:
        """Get summary of contacts"""
        return {
            'total_contacts': len(self.contacts),
            'with_emails': len([c for c in self.contacts if c.emails]),
            'with_phones': len([c for c in self.contacts if c.phones]),
            'with_companies': len([c for c in self.contacts if c.company]),
            'duplicates_found': len(self.duplicate_contacts),
            'last_sync': self.sync_history[-1]['end_time'] if self.sync_history else None
        }
        
    def get_contacts_by_source(self, source: str) -> List[Contact]:
        """Get contacts by source"""
        return [c for c in self.contacts if c.source == source]
        
    def clear_contacts(self):
        """Clear all contacts"""
        self.contacts.clear()
        self.duplicate_contacts.clear()
        self.sync_history.clear()