"""
Contact Synchronization Module
Handles contact synchronization between phone and PC.
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

from base_sync import BaseSyncModule

@dataclass
class Contact:
    """Contact data structure"""
    id: str
    first_name: str
    last_name: str
    phone_numbers: List[str]
    email_addresses: List[str]
    company: str
    job_title: str
    address: str
    notes: str
    created_date: datetime
    modified_date: datetime
    source: str  # 'phone' or 'pc'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert contact to dictionary"""
        data = asdict(self)
        data['created_date'] = self.created_date.isoformat()
        data['modified_date'] = self.modified_date.isoformat()
        return data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Contact':
        """Create contact from dictionary"""
        data['created_date'] = datetime.fromisoformat(data['created_date'])
        data['modified_date'] = datetime.fromisoformat(data['modified_date'])
        return cls(**data)

class ContactSyncModule(BaseSyncModule):
    """Contact synchronization module"""
    
    def __init__(self):
        super().__init__("contact_sync")
        self.phone_contacts = {}
        self.pc_contacts = {}
        self.sync_contacts = {}
        self.contact_id_counter = 1
        self.merge_strategy = "merge_all"
        
        # Load sample contacts
        self._load_sample_contacts()
        
    def sync_data_type(self) -> str:
        return "contacts"
        
    def _load_sample_contacts(self):
        """Load sample contacts for demonstration"""
        # Sample phone contacts
        self.phone_contacts = {
            "1": Contact(
                id="1",
                first_name="John",
                last_name="Doe",
                phone_numbers=["+1-555-0101", "+1-555-0102"],
                email_addresses=["john.doe@email.com"],
                company="Tech Corp",
                job_title="Software Engineer",
                address="123 Main St, City, State",
                notes="Work contact",
                created_date=datetime.now(),
                modified_date=datetime.now(),
                source="phone"
            ),
            "2": Contact(
                id="2",
                first_name="Jane",
                last_name="Smith",
                phone_numbers=["+1-555-0201"],
                email_addresses=["jane.smith@email.com"],
                company="Design Studio",
                job_title="UI Designer",
                address="456 Oak Ave, City, State",
                notes="Personal friend",
                created_date=datetime.now(),
                modified_date=datetime.now(),
                source="phone"
            )
        }
        
        # Sample PC contacts
        self.pc_contacts = {
            "3": Contact(
                id="3",
                first_name="Bob",
                last_name="Johnson",
                phone_numbers=["+1-555-0301"],
                email_addresses=["bob.johnson@email.com"],
                company="Marketing Inc",
                job_title="Marketing Manager",
                address="789 Pine St, City, State",
                notes="Business contact",
                created_date=datetime.now(),
                modified_date=datetime.now(),
                source="pc"
            ),
            "4": Contact(
                id="4",
                first_name="Alice",
                last_name="Brown",
                phone_numbers=["+1-555-0401", "+1-555-0402"],
                email_addresses=["alice.brown@email.com", "alice@work.com"],
                company="Consulting Group",
                job_title="Senior Consultant",
                address="321 Elm St, City, State",
                notes="Client contact",
                created_date=datetime.now(),
                modified_date=datetime.now(),
                source="pc"
            )
        }
        
        # Initialize sync contacts
        self._merge_contacts()
        
    def _merge_contacts(self):
        """Merge phone and PC contacts into sync contacts"""
        self.sync_contacts = {}
        
        # Add phone contacts
        for contact_id, contact in self.phone_contacts.items():
            sync_contact = Contact(
                id=contact_id,
                first_name=contact.first_name,
                last_name=contact.last_name,
                phone_numbers=contact.phone_numbers.copy(),
                email_addresses=contact.email_addresses.copy(),
                company=contact.company,
                job_title=contact.job_title,
                address=contact.address,
                notes=contact.notes,
                created_date=contact.created_date,
                modified_date=contact.modified_date,
                source="phone"
            )
            self.sync_contacts[contact_id] = sync_contact
            
        # Add PC contacts (check for duplicates)
        for contact_id, contact in self.pc_contacts.items():
            # Check if contact already exists (by name and phone)
            existing_contact = self._find_matching_contact(contact)
            
            if existing_contact:
                # Merge with existing contact
                self._merge_contact_data(existing_contact, contact)
            else:
                # Add as new contact
                sync_contact = Contact(
                    id=contact_id,
                    first_name=contact.first_name,
                    last_name=contact.last_name,
                    phone_numbers=contact.phone_numbers.copy(),
                    email_addresses=contact.email_addresses.copy(),
                    company=contact.company,
                    job_title=contact.job_title,
                    address=contact.address,
                    notes=contact.notes,
                    created_date=contact.created_date,
                    modified_date=contact.modified_date,
                    source="pc"
                )
                self.sync_contacts[contact_id] = sync_contact
                
    def _find_matching_contact(self, contact: Contact) -> Optional[Contact]:
        """Find matching contact in sync contacts"""
        for sync_contact in self.sync_contacts.values():
            # Check by name
            if (sync_contact.first_name.lower() == contact.first_name.lower() and
                sync_contact.last_name.lower() == contact.last_name.lower()):
                return sync_contact
                
            # Check by phone number
            for phone in contact.phone_numbers:
                if phone in sync_contact.phone_numbers:
                    return sync_contact
                    
        return None
        
    def _merge_contact_data(self, existing: Contact, new: Contact):
        """Merge new contact data with existing contact"""
        # Merge phone numbers
        for phone in new.phone_numbers:
            if phone not in existing.phone_numbers:
                existing.phone_numbers.append(phone)
                
        # Merge email addresses
        for email in new.email_addresses:
            if email not in existing.email_addresses:
                existing.email_addresses.append(email)
                
        # Update other fields if new data is more recent
        if new.modified_date > existing.modified_date:
            if new.company:
                existing.company = new.company
            if new.job_title:
                existing.job_title = new.job_title
            if new.address:
                existing.address = new.address
            if new.notes:
                existing.notes = new.notes
                
        existing.modified_date = datetime.now()
        existing.source = "merged"
        
    def get_sync_items(self) -> List[Dict[str, Any]]:
        """Get list of contacts that need synchronization"""
        sync_items = []
        
        # Check for new contacts in phone
        for contact_id, contact in self.phone_contacts.items():
            if contact_id not in self.sync_contacts:
                sync_items.append({
                    'action': 'add_contact',
                    'contact': contact,
                    'source': 'phone'
                })
                
        # Check for new contacts in PC
        for contact_id, contact in self.pc_contacts.items():
            if contact_id not in self.sync_contacts:
                sync_items.append({
                    'action': 'add_contact',
                    'contact': contact,
                    'source': 'pc'
                })
                
        # Check for updated contacts
        for contact_id in set(self.phone_contacts.keys()) & set(self.pc_contacts.keys()):
            phone_contact = self.phone_contacts[contact_id]
            pc_contact = self.pc_contacts[contact_id]
            
            if phone_contact.modified_date != pc_contact.modified_date:
                sync_items.append({
                    'action': 'update_contact',
                    'contact_id': contact_id,
                    'phone_contact': phone_contact,
                    'pc_contact': pc_contact
                })
                
        return sync_items
        
    def perform_sync(self, items: List[Dict[str, Any]]) -> bool:
        """Perform contact synchronization"""
        try:
            for item in items:
                if item['action'] == 'add_contact':
                    self._add_contact_to_sync(item['contact'])
                elif item['action'] == 'update_contact':
                    self._update_contact_in_sync(item)
                    
            # Update sync contacts
            self._merge_contacts()
            return True
            
        except Exception as e:
            self.sync_error.emit(self.name, f"Contact sync failed: {str(e)}")
            return False
            
    def _add_contact_to_sync(self, contact: Contact):
        """Add contact to sync contacts"""
        contact_id = str(self.contact_id_counter)
        self.contact_id_counter += 1
        
        sync_contact = Contact(
            id=contact_id,
            first_name=contact.first_name,
            last_name=contact.last_name,
            phone_numbers=contact.phone_numbers.copy(),
            email_addresses=contact.email_addresses.copy(),
            company=contact.company,
            job_title=contact.job_title,
            address=contact.address,
            notes=contact.notes,
            created_date=contact.created_date,
            modified_date=datetime.now(),
            source=contact.source
        )
        
        self.sync_contacts[contact_id] = sync_contact
        self.sync_activity.emit(self.name, f"Added contact: {contact.first_name} {contact.last_name}")
        
    def _update_contact_in_sync(self, item: Dict[str, Any]):
        """Update contact in sync contacts"""
        contact_id = item['contact_id']
        phone_contact = item['phone_contact']
        pc_contact = item['pc_contact']
        
        if contact_id in self.sync_contacts:
            sync_contact = self.sync_contacts[contact_id]
            
            # Merge the updated data
            self._merge_contact_data(sync_contact, phone_contact)
            self._merge_contact_data(sync_contact, pc_contact)
            
            self.sync_activity.emit(self.name, f"Updated contact: {sync_contact.first_name} {sync_contact.last_name}")
            
    def add_contact(self, contact_data: Dict[str, Any], source: str = "sync") -> str:
        """Add a new contact"""
        try:
            contact_id = str(self.contact_id_counter)
            self.contact_id_counter += 1
            
            contact = Contact(
                id=contact_id,
                first_name=contact_data.get('first_name', ''),
                last_name=contact_data.get('last_name', ''),
                phone_numbers=contact_data.get('phone_numbers', []),
                email_addresses=contact_data.get('email_addresses', []),
                company=contact_data.get('company', ''),
                job_title=contact_data.get('job_title', ''),
                address=contact_data.get('address', ''),
                notes=contact_data.get('notes', ''),
                created_date=datetime.now(),
                modified_date=datetime.now(),
                source=source
            )
            
            if source == "phone":
                self.phone_contacts[contact_id] = contact
            elif source == "pc":
                self.pc_contacts[contact_id] = contact
            else:
                self.sync_contacts[contact_id] = contact
                
            self.sync_activity.emit(self.name, f"Added new contact: {contact.first_name} {contact.last_name}")
            return contact_id
            
        except Exception as e:
            self.sync_error.emit(self.name, f"Failed to add contact: {str(e)}")
            return ""
            
    def update_contact(self, contact_id: str, contact_data: Dict[str, Any]) -> bool:
        """Update an existing contact"""
        try:
            if contact_id in self.sync_contacts:
                contact = self.sync_contacts[contact_id]
                
                # Update fields
                for field, value in contact_data.items():
                    if hasattr(contact, field) and field not in ['id', 'created_date']:
                        setattr(contact, field, value)
                        
                contact.modified_date = datetime.now()
                
                self.sync_activity.emit(self.name, f"Updated contact: {contact.first_name} {contact.last_name}")
                return True
                
            return False
            
        except Exception as e:
            self.sync_error.emit(self.name, f"Failed to update contact: {str(e)}")
            return False
            
    def delete_contact(self, contact_id: str) -> bool:
        """Delete a contact"""
        try:
            # Remove from all contact collections
            for contact_dict in [self.phone_contacts, self.pc_contacts, self.sync_contacts]:
                if contact_id in contact_dict:
                    contact = contact_dict[contact_id]
                    self.sync_activity.emit(self.name, f"Deleted contact: {contact.first_name} {contact.last_name}")
                    del contact_dict[contact_id]
                    
            return True
            
        except Exception as e:
            self.sync_error.emit(self.name, f"Failed to delete contact: {str(e)}")
            return False
            
    def search_contacts(self, query: str) -> List[Contact]:
        """Search contacts by name, phone, or email"""
        results = []
        query_lower = query.lower()
        
        for contact in self.sync_contacts.values():
            # Search by name
            if (query_lower in contact.first_name.lower() or
                query_lower in contact.last_name.lower()):
                results.append(contact)
                continue
                
            # Search by phone number
            for phone in contact.phone_numbers:
                if query_lower in phone:
                    results.append(contact)
                    break
                    
            # Search by email
            for email in contact.email_addresses:
                if query_lower in email.lower():
                    results.append(contact)
                    break
                    
        return results
        
    def get_contact_stats(self) -> Dict[str, Any]:
        """Get contact synchronization statistics"""
        return {
            'total_contacts': len(self.sync_contacts),
            'phone_contacts': len(self.phone_contacts),
            'pc_contacts': len(self.pc_contacts),
            'merged_contacts': len([c for c in self.sync_contacts.values() if c.source == "merged"]),
            'last_sync': self.last_sync_time
        }
        
    def export_contacts(self, file_path: str, format_type: str = "json") -> bool:
        """Export contacts to file"""
        try:
            if format_type == "json":
                data = {
                    'contacts': [contact.to_dict() for contact in self.sync_contacts.values()],
                    'export_time': datetime.now().isoformat()
                }
                
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
                    
            elif format_type == "csv":
                import csv
                
                with open(file_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    # Write header
                    writer.writerow(['First Name', 'Last Name', 'Phone Numbers', 'Email Addresses', 
                                   'Company', 'Job Title', 'Address', 'Notes'])
                    
                    # Write contacts
                    for contact in self.sync_contacts.values():
                        writer.writerow([
                            contact.first_name,
                            contact.last_name,
                            '; '.join(contact.phone_numbers),
                            '; '.join(contact.email_addresses),
                            contact.company,
                            contact.job_title,
                            contact.address,
                            contact.notes
                        ])
                        
            self.sync_activity.emit(self.name, f"Exported contacts to {file_path}")
            return True
            
        except Exception as e:
            self.sync_error.emit(self.name, f"Failed to export contacts: {str(e)}")
            return False
            
    def import_contacts(self, file_path: str, format_type: str = "json") -> bool:
        """Import contacts from file"""
        try:
            if format_type == "json":
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                for contact_data in data.get('contacts', []):
                    contact = Contact.from_dict(contact_data)
                    self.sync_contacts[contact.id] = contact
                    
            elif format_type == "csv":
                import csv
                
                with open(file_path, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        contact_data = {
                            'first_name': row['First Name'],
                            'last_name': row['Last Name'],
                            'phone_numbers': row['Phone Numbers'].split('; ') if row['Phone Numbers'] else [],
                            'email_addresses': row['Email Addresses'].split('; ') if row['Email Addresses'] else [],
                            'company': row['Company'],
                            'job_title': row['Job Title'],
                            'address': row['Address'],
                            'notes': row['Notes']
                        }
                        
                        self.add_contact(contact_data, "import")
                        
            self.sync_activity.emit(self.name, f"Imported contacts from {file_path}")
            return True
            
        except Exception as e:
            self.sync_error.emit(self.name, f"Failed to import contacts: {str(e)}")
            return False