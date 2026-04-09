import re
import time
from playwright.sync_api import sync_playwright

FOLDER_URL = "https://auckland.au.panopto.com/Panopto/Pages/Sessions/List.aspx?embedded=0&isFromTeams=false#endDate=%2201%2F02%2F2025%22"
BASE_URL = "https://auckland.au.panopto.com"

def main():
    with sync_playwright() as p:
        # Launch a visible browser so you can log in
        browser = p.chromium.launch(headless=False)
        
        #   Enable downloads in the browser context
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        print("Navigating to Panopto...")
        page.goto(FOLDER_URL)

        print("\n*** MANUAL STEPS REQUIRED ***")
        print("1. Please log in with your university credentials in the browser window.")
        print("2. Once logged in and on the folder page, SCROLL DOWN to the very bottom.")
        print("3. Ensure ALL videos you want to download are visible on the screen.")
        input("Press ENTER here in the terminal when you are ready to continue...")

        # Find all anchor tags that link to the video viewer
        links = page.locator('a[href*="Viewer.aspx?id="]').evaluate_all('elements => elements.map(e => e.href)')
        
        video_ids = []
        for link in links:
            # Extract the UUID from the URL
            match = re.search(r'id=([a-f0-9\-]+)', link)
            if match:
                video_ids.append(match.group(1))

        # Remove duplicates
        video_ids = list(set(video_ids))
        print(f"\nFound {len(video_ids)} unique videos to download.")

        # Loop through and download
        for index, vid_id in enumerate(video_ids, start=1):
            # Construct the download URL based on your network analysis
            download_url = f"{BASE_URL}/Panopto/Podcast/Download/{vid_id}.mp4?mediaTargetType=videoPodcast"
            print(f"[{index}/{len(video_ids)}] Starting download for video ID: {vid_id}...")
            
            try:
                # Tell Playwright to expect a file download
                with page.expect_download(timeout=60000) as download_info:
                    # FIX: Use JavaScript to trigger the navigation.
                    # This stops Playwright from throwing the strict navigation error.
                    page.evaluate(f"window.location.href = '{download_url}'")

                download = download_info.value

                # Grab the actual filename from the server (e.g., "MEDSCI 300 Final Project.mp4")
                file_name = download.suggested_filename
                print(f"  -> Downloading {file_name}... (this may take a moment)")

                # Save the file to your current folder
                download.save_as(file_name)
                print(f"  -> Successfully saved: {file_name}")

                # Pause for a few seconds so Panopto doesn't rate-limit you for spamming 234 downloads
                time.sleep(3)

            except Exception as e:
                print(f"  -> Failed to download {vid_id}: {e}")

        print("\nAll downloads completed!")
        browser.close()

if __name__ == "__main__":
    main()