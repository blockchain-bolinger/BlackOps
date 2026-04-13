#!/usr/bin/env python3
"""
CloudRaider - Cloud Security Assessment Tool
NUR FÜR AUTORISIERTE TESTS! Prüft öffentliche Buckets, IAM Fehlkonfigurationen uvm.
"""

import argparse
import requests
import boto3
import json
import sys
import os
from colorama import Fore, init
from botocore.exceptions import ClientError, NoCredentialsError

# Für Azure und GCP
try:
    from azure.storage.blob import BlobServiceClient
    from google.cloud import storage
    AZURE_GCP_AVAILABLE = True
except ImportError:
    AZURE_GCP_AVAILABLE = False

init(autoreset=True)

class CloudRaider:
    def __init__(self, target=None, aws_profile=None, output=None):
        self.target = target  # Kann S3-Bucket-Name, Azure Storage-Name, Domain sein
        self.aws_profile = aws_profile
        self.output_file = output
        self.results = {"findings": [], "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}
        
    def print_banner(self):
        print(rf"""{Fore.BLUE}
   ____ _                 _     _       _          
  / ___| | ___  _   _  __| | __| | __ _| |_ ___  _ 
 | |   | |/ _ \| | | |/ _` |/ _` |/ _` | __/ _ \/ |
 | |___| | (_) | |_| | (_| | (_| | (_| | ||  __/| |
  \____|_|\___/ \__,_|\__,_|\__,_|\__,_|\__\___|_ |
{Fore.WHITE}   >> CLOUD SECURITY SCANNER v1.0 <<
{Fore.YELLOW}   NUR FÜR AUTORISIERTE TESTS!
        """)
    
    # ---------- AWS ----------
    def check_s3_bucket_public(self, bucket_name):
        """Prüft, ob ein S3-Bucket öffentlich ist"""
        try:
            session = boto3.Session(profile_name=self.aws_profile) if self.aws_profile else boto3.Session()
            s3 = session.client('s3')
            # Versuche Liste der Objekte (ohne Berechtigung -> Fehler)
            try:
                s3.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
                # Kein Fehler -> Bucket ist mindestens öffentlich lesbar
                self.results["findings"].append({
                    "service": "AWS S3",
                    "bucket": bucket_name,
                    "issue": "Bucket ist öffentlich lesbar (list objects allowed)",
                    "severity": "HIGH"
                })
                print(f"{Fore.RED}[!] S3 Bucket {bucket_name} ist öffentlich lesbar!")
            except ClientError as e:
                if e.response['Error']['Code'] == 'AccessDenied':
                    # Prüfe, ob Bucket öffentlich schreibbar ist
                    try:
                        # Versuche Objekt hochzuladen (Test)
                        s3.put_object(Bucket=bucket_name, Key='test.txt', Body=b'test')
                        self.results["findings"].append({
                            "service": "AWS S3",
                            "bucket": bucket_name,
                            "issue": "Bucket ist öffentlich schreibbar",
                            "severity": "CRITICAL"
                        })
                        print(f"{Fore.RED}[!] S3 Bucket {bucket_name} ist öffentlich SCHREIBBAR!")
                    except:
                        pass
                else:
                    print(f"{Fore.YELLOW}[i] Bucket {bucket_name} nicht öffentlich.")
        except NoCredentialsError:
            print(f"{Fore.YELLOW}[!] Keine AWS Credentials gefunden. Überspringe S3-Check.")
        except Exception as e:
            print(f"{Fore.RED}[!] Fehler: {e}")
    
    def check_iam_users(self):
        """Prüft IAM-Benutzer ohne MFA"""
        try:
            session = boto3.Session(profile_name=self.aws_profile) if self.aws_profile else boto3.Session()
            iam = session.client('iam')
            users = iam.list_users()['Users']
            for user in users:
                username = user['UserName']
                # Prüfe MFA Geräte
                mfa = iam.list_mfa_devices(UserName=username)['MFADevices']
                if not mfa:
                    self.results["findings"].append({
                        "service": "AWS IAM",
                        "user": username,
                        "issue": "Kein MFA aktiviert",
                        "severity": "MEDIUM"
                    })
                    print(f"{Fore.YELLOW}[!] IAM User {username} hat kein MFA!")
        except:
            pass
    
    # ---------- Azure ----------
    def check_azure_blob_public(self, storage_account):
        """Prüft, ob ein Azure Blob Container öffentlich ist"""
        if not AZURE_GCP_AVAILABLE:
            print(f"{Fore.YELLOW}[!] Azure SDK nicht installiert. Überspringe Azure-Check.")
            return
        try:
            blob_service_client = BlobServiceClient(account_url=f"https://{storage_account}.blob.core.windows.net", credential=None)
            containers = blob_service_client.list_containers()
            for container in containers:
                # Prüfe ACL
                acl = blob_service_client.get_container_access_policy(container.name)
                if acl.get('public_access') != 'off':
                    self.results["findings"].append({
                        "service": "Azure Blob",
                        "container": container.name,
                        "issue": f"Öffentlicher Zugriff: {acl['public_access']}",
                        "severity": "HIGH"
                    })
                    print(f"{Fore.RED}[!] Azure Blob Container {container.name} ist öffentlich!")
        except Exception as e:
            print(f"{Fore.YELLOW}[i] Azure Check fehlgeschlagen: {e}")
    
    # ---------- GCP ----------
    def check_gcp_bucket_public(self, bucket_name):
        """Prüft, ob ein GCS Bucket öffentlich ist"""
        if not AZURE_GCP_AVAILABLE:
            print(f"{Fore.YELLOW}[!] GCP SDK nicht installiert. Überspringe GCP-Check.")
            return
        try:
            client = storage.Client()
            bucket = client.get_bucket(bucket_name)
            # Prüfe IAM Policies
            policy = bucket.get_iam_policy()
            for role, members in policy.items():
                if 'allUsers' in members or 'allAuthenticatedUsers' in members:
                    self.results["findings"].append({
                        "service": "GCP Storage",
                        "bucket": bucket_name,
                        "issue": f"Bucket ist öffentlich (Role: {role})",
                        "severity": "HIGH"
                    })
                    print(f"{Fore.RED}[!] GCP Bucket {bucket_name} ist öffentlich!")
        except Exception as e:
            print(f"{Fore.YELLOW}[i] GCP Check fehlgeschlagen: {e}")
    
    # ---------- Domain-basierte Cloud-Erkennung ----------
    def analyze_domain(self, domain):
        """Analysiert eine Domain auf Cloud-Ressourcen (z.B. S3-Bucket-URLs)"""
        # Suche nach S3-Bucket-URLs im HTML/JS
        try:
            resp = requests.get(f"http://{domain}", timeout=5)
            # Einfache Regex für S3-Bucket-Namen in URLs
            s3_pattern = r'(https?://)?([a-zA-Z0-9\-]+)\.s3\.([a-z\-]+\.)?amazonaws\.com'
            matches = re.findall(s3_pattern, resp.text)
            for match in matches:
                bucket_name = match[1]
                self.check_s3_bucket_public(bucket_name)
        except:
            pass
    
    def run(self):
        self.print_banner()
        print(f"{Fore.WHITE}[*] Ziel: {self.target}")
        if self.target.startswith("s3://") or '.' in self.target and 'amazonaws' in self.target:
            # S3 Bucket
            bucket = self.target.replace("s3://", "").split('/')[0]
            self.check_s3_bucket_public(bucket)
        elif 'blob.core.windows.net' in self.target:
            # Azure
            account = self.target.split('.')[0]
            self.check_azure_blob_public(account)
        elif 'storage.googleapis.com' in self.target:
            # GCP
            bucket = self.target.split('/')[2]
            self.check_gcp_bucket_public(bucket)
        else:
            # Domain
            self.analyze_domain(self.target)
        
        # Zusätzliche Checks (wenn AWS Credentials vorhanden)
        self.check_iam_users()
        
        if self.output_file:
            with open(self.output_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"{Fore.GREEN}[✓] Ergebnisse gespeichert: {self.output_file}")
        else:
            print(json.dumps(self.results, indent=2))

def main():
    parser = argparse.ArgumentParser(description="CloudRaider - Cloud Security Checker")
    parser.add_argument("target", help="S3-Bucket-Name, Azure Storage-Name, GCS-Bucket oder Domain")
    parser.add_argument("--aws-profile", help="AWS Profilname")
    parser.add_argument("-o", "--output", help="JSON-Output Datei")
    args = parser.parse_args()
    
    print(f"{Fore.RED}[!] CloudRaider: Nur für autorisierte Tests!")
    confirm = input(f"{Fore.WHITE}[?] Fortfahren? (ja/NEIN): ").strip().lower()
    if confirm != "ja":
        print("Abbruch.")
        sys.exit(0)
    
    raider = CloudRaider(args.target, args.aws_profile, args.output)
    raider.run()

if __name__ == "__main__":
    import time
    import re
    main()
