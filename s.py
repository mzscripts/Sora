import os
import re
import requests

def download_images(input_file, output_folder):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Regular expression pattern for URLs
    url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
    
    try:
        # Read the input text file
        with open(input_file, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Find all URLs in the content
        urls = re.findall(url_pattern, content)
        
        # Download each image
        for i, url in enumerate(urls):
            try:
                # Get the image content
                response = requests.get(url, stream=True)
                
                # Check if the response is an image
                if response.status_code == 200 and 'image' in response.headers.get('content-type', ''):
                    # Create filename
                    filename = os.path.join(output_folder, f'image_{i+1}.png')
                    
                    # Save the image
                    with open(filename, 'wb') as f:
                        for chunk in response.iter_content(1024):
                            f.write(chunk)
                    print(f'Successfully downloaded: {filename}')
                else:
                    print(f'Skipped non-image URL: {url}')
                    
            except Exception as e:
                print(f'Error downloading {url}: {str(e)}')
                
    except Exception as e:
        print(f'Error reading file {input_file}: {str(e)}')

if __name__ == '__main__':
    input_file = 'input.txt'  # Path to your input text file
    output_folder = 'motu'  # Path to save images
    download_images(input_file, output_folder)