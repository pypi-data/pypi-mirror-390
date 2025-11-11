#!/usr/bin/env python3
"""
LFM License Verification System
Helps businesses integrate license verification
"""

import os
import json
import hashlib
import datetime
from pathlib import Path
from typing import Optional, Dict

class LFMLicenseManager:
    """
    License management for LFM AI Upgrade System
    
    For businesses: This shows how to verify your commercial license
    For individuals: No verification needed, just use it!
    """
    
    def __init__(self):
        self.license_file = Path.home() / ".lfm" / "license.json"
        self.trial_file = Path.home() / ".lfm" / "trial.json"
        
    def check_license(self) -> Dict:
        """
        Check license status
        Returns dict with status and details
        """
        # First, check for commercial license
        if self.license_file.exists():
            return self._verify_commercial_license()
        
        # Check for trial
        if self.trial_file.exists():
            return self._check_trial_status()
        
        # No license file = assume individual/student use
        return {
            'status': 'community',
            'type': 'Individual/Student',
            'valid': True,
            'message': 'Community license - free for personal/educational use',
            'restrictions': 'No commercial use permitted'
        }
    
    def _verify_commercial_license(self) -> Dict:
        """Verify commercial license file"""
        try:
            with open(self.license_file, 'r') as f:
                license_data = json.load(f)
            
            # Check expiration
            exp_date = datetime.datetime.fromisoformat(license_data.get('expires', '2000-01-01'))
            if exp_date < datetime.datetime.now():
                return {
                    'status': 'expired',
                    'type': 'Commercial',
                    'valid': False,
                    'message': 'Commercial license expired',
                    'action': 'Contact keith@thenewfaithchurch.org for renewal'
                }
            
            # Verify signature (simplified)
            expected_sig = self._generate_signature(license_data)
            if license_data.get('signature') != expected_sig:
                return {
                    'status': 'invalid',
                    'type': 'Commercial',
                    'valid': False,
                    'message': 'Invalid license signature',
                    'action': 'Contact keith@thenewfaithchurch.org'
                }
            
            return {
                'status': 'commercial',
                'type': license_data.get('tier', 'Commercial'),
                'valid': True,
                'company': license_data.get('company'),
                'expires': license_data.get('expires'),
                'message': 'Valid commercial license'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'valid': False,
                'message': f'License verification error: {e}'
            }
    
    def _check_trial_status(self) -> Dict:
        """Check trial period status"""
        try:
            with open(self.trial_file, 'r') as f:
                trial_data = json.load(f)
            
            start_date = datetime.datetime.fromisoformat(trial_data.get('started'))
            days_elapsed = (datetime.datetime.now() - start_date).days
            
            if days_elapsed > 30:
                return {
                    'status': 'trial_expired',
                    'valid': False,
                    'message': f'30-day trial expired ({days_elapsed} days)',
                    'action': 'Purchase commercial license at keith@thenewfaithchurch.org'
                }
            
            return {
                'status': 'trial',
                'valid': True,
                'days_remaining': 30 - days_elapsed,
                'message': f'Trial period - {30 - days_elapsed} days remaining',
                'action': 'Contact keith@thenewfaithchurch.org to purchase'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'valid': False,
                'message': f'Trial verification error: {e}'
            }
    
    def start_trial(self, company_name: str, contact_email: str) -> bool:
        """
        Start a 30-day trial for businesses
        """
        self.trial_file.parent.mkdir(parents=True, exist_ok=True)
        
        trial_data = {
            'company': company_name,
            'email': contact_email,
            'started': datetime.datetime.now().isoformat(),
            'type': 'trial'
        }
        
        with open(self.trial_file, 'w') as f:
            json.dump(trial_data, f, indent=2)
        
        print(f"""
✅ 30-Day Trial Started!

Company: {company_name}
Contact: {contact_email}
Expires: {(datetime.datetime.now() + datetime.timedelta(days=30)).strftime('%Y-%m-%d')}

You have full access to LFM AI Upgrade System for 30 days.
To purchase a commercial license, contact: keith@thenewfaithchurch.org

Thank you for trying LFM!
        """)
        return True
    
    def install_license(self, license_key: str) -> bool:
        """
        Install a commercial license
        License keys are provided after purchase
        """
        try:
            # Decode the license key (base64 encoded JSON)
            import base64
            license_json = base64.b64decode(license_key).decode('utf-8')
            license_data = json.loads(license_json)
            
            # Verify the license is valid
            if self._validate_license_data(license_data):
                self.license_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.license_file, 'w') as f:
                    json.dump(license_data, f, indent=2)
                
                print(f"""
✅ Commercial License Installed Successfully!

Company: {license_data.get('company')}
Tier: {license_data.get('tier')}
Expires: {license_data.get('expires')}

Thank you for supporting LFM development!
                """)
                return True
            else:
                print("❌ Invalid license key")
                return False
                
        except Exception as e:
            print(f"❌ Error installing license: {e}")
            return False
    
    def _validate_license_data(self, data: Dict) -> bool:
        """Validate license data structure"""
        required_fields = ['company', 'tier', 'expires', 'signature']
        return all(field in data for field in required_fields)
    
    def _generate_signature(self, data: Dict) -> str:
        """Generate signature for license validation"""
        # Simplified signature - in production use cryptographic signing
        sig_string = f"{data.get('company')}-{data.get('expires')}-LFM"
        return hashlib.sha256(sig_string.encode()).hexdigest()[:16]

def print_license_info():
    """
    Print clear licensing information for users
    """
    print("""
╔══════════════════════════════════════════════════════════╗
║         LFM AI UPGRADE SYSTEM - LICENSE INFO              ║
╠══════════════════════════════════════════════════════════╣
║                                                            ║
║  🎓 FREE FOR:                                              ║
║     • Individuals (personal projects)                     ║
║     • Students (all educational use)                      ║
║     • Academics (research & teaching)                     ║
║     • Open source (non-commercial)                        ║
║                                                            ║
║  💼 COMMERCIAL LICENSE REQUIRED FOR:                      ║
║     • Businesses of any size                              ║
║     • Commercial products/services                        ║
║     • Consulting or client work                           ║
║     • Revenue-generating activities                       ║
║                                                            ║
║  📧 GET COMMERCIAL LICENSE:                               ║
║     Email: keith@thenewfaithchurch.org                   ║
║     Pricing:                                               ║
║       - Startup (<$1M): $2,500/year                      ║
║       - Small ($1M-$10M): $5,000/year                    ║
║       - Medium ($10M-$100M): $25,000/year                ║
║       - Enterprise (>$100M): $100,000/year               ║
║                                                            ║
║  🔧 30-DAY FREE TRIAL:                                    ║
║     Businesses can evaluate for 30 days free             ║
║                                                            ║
╚══════════════════════════════════════════════════════════╝
    """)

def main():
    """Main entry point for license management"""
    import sys
    
    manager = LFMLicenseManager()
    
    if len(sys.argv) < 2:
        print_license_info()
        status = manager.check_license()
        print(f"\nCurrent Status: {status['message']}")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'check':
        status = manager.check_license()
        print(json.dumps(status, indent=2))
    
    elif command == 'trial':
        if len(sys.argv) < 4:
            print("Usage: python license_manager.py trial <company_name> <email>")
        else:
            manager.start_trial(sys.argv[2], sys.argv[3])
    
    elif command == 'install':
        if len(sys.argv) < 3:
            print("Usage: python license_manager.py install <license_key>")
        else:
            manager.install_license(sys.argv[2])
    
    elif command == 'info':
        print_license_info()
    
    else:
        print(f"Unknown command: {command}")
        print("Commands: check, trial, install, info")

if __name__ == "__main__":
    main()
