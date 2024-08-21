import os
from bs4 import BeautifulSoup

def extract_links_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    # Find all <a> elements within divs that have class "kgrOn o"
    elements = soup.find_all("div", class_="kgrOn o")
    links = []
    for element in elements:
        link_tag = element.find("a", href=True)
        if link_tag:
            # Extract the href attribute (the link) and strip any surrounding whitespace
            links.append(link_tag['href'].strip())
    return links

def extract_links_from_files(directory):
    all_links = []
    # Iterate through all .txt files in the given directory
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
                links = extract_links_from_html(content)
                all_links.extend(links)
    return all_links

def write_links_to_file(links, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        for link in links:
            file.write("https://www.tripadvisor.com/" + link + '\n')

# Example usage
directory_path = 'do\\links'  # Replace with the path to your .txt files
output_file_path = 'combine.txt'  # The output file to store the links

extracted_links = extract_links_from_files(directory_path)
write_links_to_file(extracted_links, directory_path + "\\" + output_file_path)

print(f"All links have been written to {output_file_path}")
