import requests
import numpy as np
import time

# Define your modified function to fetch 'code' for a given business ID
def fetch_business_line_prh(business_id):
    url = f'https://avoindata.prh.fi/bis/v1/{business_id}'
    max_retries = 3

    for retry in range(max_retries):
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            business_lines = data['results'][0].get('businessLines', [])[0].get('code', '-1')
            return business_lines
        elif response.status_code == 503:
            # Handle rate limiting by retrying the request
            if retry < max_retries - 1:
                print(f'Received 503. Retrying in 1 minute (Retry {retry + 1}/{max_retries})...')
                time.sleep(60)  # Pause for 1 minute before retrying
            else:
                print(f'Received 503. Maximum retry attempts reached. Giving up.')
                return '-1'
        else:
            print(f'Failed to fetch data for business ID: {business_id}, status code: {response.status_code}')
            return '-1'

if __name__ == "__main__":
    # Load from npy file
    business_ids = np.load('./data/tax_data/missing_business_line.npy').tolist()
    # business_ids = business_ids[:100000]  # Adjust the number of rows as needed

    batch_size = 1000
    pause_duration = 120  # 2 minutes

    results = []

    for i in range(93000, len(business_ids), batch_size):
        batch = business_ids[i:i + batch_size]
        code = []

        for business_id in batch:
            result = fetch_business_line_prh(business_id)
            code.append(result)
        
        results.extend(code)

        # Save code to a separate .npy file with an index-based name
        file_name = f'./data/tax_data/fill_business_line_{i}.npy'
        np.save(file_name, code)
        
        # Introduce a pause between batches
        if i + batch_size < len(business_ids):
            print(f"Processed {i + batch_size} business IDs. Pausing for {pause_duration} seconds...")
            time.sleep(pause_duration)


    print(results)
    print(len(results))

    code = np.array(results)
    # Save the final code to a .npy file
    np.save('./data/tax_data/fill_business_line.npy', code)
    # Count the number of -1 values
    missing_count = len(code[code == '-1'])
    # Print the number of missing values
    print(f'Number of missing values: {missing_count}')
    print(f'Proportion of missing values: {missing_count / len(code)}')
