import asyncio
from aiohttp import ClientSession
import numpy as np
import time


# Define your modified function to fetch 'code' for a given business ID
async def fetch_business_line_prh(business_id, session):
    url = f'https://avoindata.prh.fi/bis/v1/{business_id}'
    async with session.get(url) as response:
        if response.status == 200:
            data = await response.json()
            business_lines = data['results'][0].get('businessLines', [])[0].get('code', np.nan)
            return business_lines
        elif response.status == 503:
            # Handle rate limiting by retrying the request
            return 503
        else:
            print(f'Failed to fetch data for business ID: {business_id}, status code: {response.status}')
            return -1


async def bound_fetch(sem, business_id, session, max_retries=5):
    for _ in range(max_retries):
        async with sem:
            response = await fetch_business_line_prh(business_id, session)
            if response != 503:  # Check for rate limiting
                return response
            else:
                await asyncio.sleep(5)  # Wait for a while before retrying
    return -1


async def main(business_ids):
    tasks = []
    sem = asyncio.Semaphore(10)  # Adjust the semaphore limit as needed

    async with ClientSession() as session:
        for business_id in business_ids:
            task = asyncio.ensure_future(bound_fetch(sem, business_id, session))
            tasks.append(task)

        results = await asyncio.gather(*tasks)

    return results


if __name__ == "__main__":
    # Load from npy file
    business_ids = np.load('./data/tax_data/missing_business_line.npy').tolist()
    business_ids = business_ids[:100000]  # Adjust the number of rows as needed

    batch_size = 500
    pause_duration = 120  # 2 minutes

    results = []

    for i in range(66000, len(business_ids), batch_size):
        print(f'Processing business IDs {i} to {i + batch_size}...')
        batch = business_ids[i:i + batch_size]
        code = asyncio.run(main(batch))

        results.extend(code)

        # Save code to a separate .npy file with an index-based name
        code = np.array(code)
        filename = f'./data/tax_data/fill_business_line/iteration_{i}.npy'
        np.save(filename, code)
        
        # Introduce a pause between batches
        if i + batch_size < len(business_ids):
            print(f"Processed {i + batch_size} business IDs. Pausing for {pause_duration} seconds...")
            time.sleep(pause_duration)
            # asyncio.run(asyncio.sleep(pause_duration))

    print(results)
    print(len(results))

    results = np.array(results)
    # Save the final code to a .npy file
    np.save('./data/tax_data/fill_business_line/fill_business_line_100000.npy', results)
    # Count the number of -1 values
    missing_count = len(results[results == '-1'])
    # Print the number of missing values
    print(f'Number of missing values: {missing_count}')
    print(f'Proportion of missing values: {missing_count / len(results)}')

