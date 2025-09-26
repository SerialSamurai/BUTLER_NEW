"""
BUTLER Complex Demo Scenario
Demonstrates multi-system threat correlation and automated response
"""

import sqlite3
import json
from datetime import datetime, timedelta
import random

def create_complex_scenario():
    """Create a coordinated threat scenario for demo"""

    # Connect to databases
    email_conn = sqlite3.connect('butler_emails.db')
    crime_conn = sqlite3.connect('crime_intelligence.db')

    email_cursor = email_conn.cursor()
    crime_cursor = crime_conn.cursor()

    # Create emails table if not exists
    email_cursor.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            subject TEXT,
            body TEXT,
            threat_score INTEGER,
            timestamp TEXT,
            status TEXT DEFAULT 'unread'
        )
    """)

    # Scenario: Coordinated gang activity with cyber component
    base_time = datetime.now()

    # 1. Create suspicious email pattern
    suspicious_emails = [
        {
            'sender': 'unknown_428@protonmail.com',
            'subject': 'Meeting confirmed - Oak Cliff location',
            'body': 'Everyone needs to be there at 2am. Bring the packages discussed.',
            'threat_score': 85,
            'timestamp': (base_time - timedelta(hours=12)).isoformat()
        },
        {
            'sender': 'throwaway9821@tutanota.com',
            'subject': 'RE: Equipment ready',
            'body': 'Got the tools from the supplier. South Dallas dropoff point active.',
            'threat_score': 78,
            'timestamp': (base_time - timedelta(hours=8)).isoformat()
        },
        {
            'sender': 'dallas_watch_823@gmail.com',
            'subject': 'Unusual activity - multiple reports',
            'body': 'Citizens reporting suspicious vehicles near Jefferson and Beckley. Multiple black SUVs.',
            'threat_score': 72,
            'timestamp': (base_time - timedelta(hours=4)).isoformat()
        },
        {
            'sender': 'alert@ringcentral.com',
            'subject': 'Multiple security cameras triggered',
            'body': 'Unusual pattern detected: 15 cameras triggered sequentially along Industrial Blvd',
            'threat_score': 90,
            'timestamp': (base_time - timedelta(hours=2)).isoformat()
        },
        {
            'sender': 'dpd_tip_line@dallascityhall.com',
            'subject': 'Anonymous tip - URGENT',
            'body': 'Large gathering planned tonight. Possible gang initiation. Oak Cliff area.',
            'threat_score': 95,
            'timestamp': (base_time - timedelta(minutes=30)).isoformat()
        }
    ]

    # Insert suspicious emails
    for email in suspicious_emails:
        email_cursor.execute("""
            INSERT INTO emails (sender, subject, body, threat_score, timestamp, status)
            VALUES (?, ?, ?, ?, ?, 'flagged')
        """, (email['sender'], email['subject'], email['body'],
              email['threat_score'], email['timestamp']))

    # 2. Create correlated crime data
    crime_incidents = [
        {
            'type': 'BURGLARY',
            'location': 'Oak Cliff - Jefferson Blvd',
            'description': 'Pattern of break-ins, professional crew suspected',
            'severity': 'HIGH',
            'timestamp': (base_time - timedelta(days=3)).isoformat()
        },
        {
            'type': 'WEAPONS',
            'location': 'South Dallas - MLK Jr Blvd',
            'description': 'Illegal firearms transaction reported',
            'severity': 'CRITICAL',
            'timestamp': (base_time - timedelta(days=2)).isoformat()
        },
        {
            'type': 'GANG_ACTIVITY',
            'location': 'Oak Cliff - Kiest Park',
            'description': 'Known gang members spotted, unusual gathering',
            'severity': 'HIGH',
            'timestamp': (base_time - timedelta(hours=6)).isoformat()
        },
        {
            'type': 'SURVEILLANCE',
            'location': 'Industrial District',
            'description': 'Multiple vehicles casing warehouses',
            'severity': 'MEDIUM',
            'timestamp': (base_time - timedelta(hours=3)).isoformat()
        }
    ]

    # Drop and recreate crime incidents table
    crime_cursor.execute("DROP TABLE IF EXISTS incidents")
    crime_cursor.execute("""
        CREATE TABLE incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            location TEXT,
            description TEXT,
            severity TEXT,
            timestamp TEXT,
            status TEXT DEFAULT 'active'
        )
    """)

    for incident in crime_incidents:
        crime_cursor.execute("""
            INSERT INTO incidents (type, location, description, severity, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (incident['type'], incident['location'], incident['description'],
              incident['severity'], incident['timestamp']))

    # 3. Create correlation analysis
    crime_cursor.execute("""
        CREATE TABLE IF NOT EXISTS threat_correlations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_name TEXT,
            confidence INTEGER,
            involved_systems TEXT,
            recommended_action TEXT,
            timestamp TEXT
        )
    """)

    correlation = {
        'pattern_name': 'Coordinated Gang Operation - Oak Cliff',
        'confidence': 92,
        'involved_systems': json.dumps(['Email Monitor', 'Crime Database', 'Camera Network', 'Tip Line']),
        'recommended_action': 'IMMEDIATE: Deploy units to Oak Cliff. Setup perimeter at Jefferson/Beckley. Alert SWAT standby.',
        'timestamp': base_time.isoformat()
    }

    crime_cursor.execute("""
        INSERT INTO threat_correlations (pattern_name, confidence, involved_systems, recommended_action, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (correlation['pattern_name'], correlation['confidence'],
          correlation['involved_systems'], correlation['recommended_action'],
          correlation['timestamp']))

    email_conn.commit()
    crime_conn.commit()

    print("[SUCCESS] Complex threat scenario created!")
    print("\n[DEMO] Talking Points:")
    print("1. Show how BUTLER detected pattern across multiple systems")
    print("2. Point out the increasing threat scores over time")
    print("3. Demonstrate the correlation confidence (92%)")
    print("4. Show the automated recommended response")
    print("\n[QUERIES] Try these in the chat:")
    print('- "Analyze recent gang activity"')
    print('- "Show threat correlations"')
    print('- "What\'s happening in Oak Cliff?"')
    print('- "Generate tactical response plan"')

    email_conn.close()
    crime_conn.close()

if __name__ == "__main__":
    create_complex_scenario()