import subprocess

def list_voices():
    ps_code = """
    $voice = New-Object -ComObject SAPI.SpVoice
    $voice.GetVoices() | ForEach-Object { 
        Write-Output "Name: $($_.GetDescription())"
        Write-Output "ID: $($_.Id)"
        Write-Output "----------------"
    }
    """
    cmd = ["powershell.exe", "-Command", ps_code]
    
    print("Querying SAPI voices via PowerShell...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running PowerShell: {e}")
        print(f"Stderr: {e.stderr}")
    except FileNotFoundError:
        print("powershell.exe not found.")

if __name__ == "__main__":
    list_voices()
