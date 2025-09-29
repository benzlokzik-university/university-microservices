#!/usr/bin/env python3
"""
Split the large SVG into 6 bounded contexts (microservices)
"""
import xml.etree.ElementTree as ET
import re

# Parse the SVG
tree = ET.parse("Микросервисы 1.svg")
root = tree.getroot()

# Define the namespaces
ns = {'svg': 'http://www.w3.org/2000/svg'}
ET.register_namespace('', 'http://www.w3.org/2000/svg')

# Find all bounded context rectangles by looking for the gray boxes with text labels
contexts = []

# Find all groups with stroke-linecap="round" which represent the bounded contexts
for g in root.findall('.//{http://www.w3.org/2000/svg}g[@stroke-linecap="round"]'):
    transform = g.get('transform', '')
    # Extract translate values
    match = re.search(r'translate\(([\d.]+)\s+([\d.]+)\)', transform)
    if match:
        x = float(match.group(1))
        y = float(match.group(2))
        
        # Find the text label (next sibling)
        parent = root
        for elem in root.iter():
            for child in elem:
                if child == g:
                    # Find the next sibling that has text
                    idx = list(elem).index(g)
                    if idx + 1 < len(list(elem)):
                        next_elem = list(elem)[idx + 1]
                        text_elem = next_elem.find('.//{http://www.w3.org/2000/svg}text')
                        if text_elem is not None and text_elem.text:
                            # Get the path to find width
                            path = g.find('.//{http://www.w3.org/2000/svg}path')
                            if path is not None:
                                # Extract width from rotate parameters
                                rotate_match = re.search(r'rotate\(0\s+([\d.]+)\s+([\d.]+)\)', transform)
                                if rotate_match:
                                    width = float(rotate_match.group(1)) * 2
                                    height = float(rotate_match.group(2)) * 2
                                    contexts.append({
                                        'name': text_elem.text.strip(),
                                        'x': x,
                                        'y': y,
                                        'width': width,
                                        'height': height
                                    })
                    break

# Sort by x position
contexts.sort(key=lambda c: c['x'])

# Print found contexts
print("Found bounded contexts:")
for i, ctx in enumerate(contexts, 1):
    print(f"{i}. {ctx['name']} at x={ctx['x']:.1f}, width={ctx['width']:.1f}")

# Define regions manually based on detected bounded contexts
# Using detected positions with adjusted widths to avoid overlap
regions = [
    {'name': 'Аккаунт пользователя', 'x': 18, 'width': 820},           # 18.6 to ~838
    {'name': 'Каталог игр', 'x': 865, 'width': 1170},                  # 865.7 to ~2035
    {'name': 'Бронирование', 'x': 2056, 'width': 310},                 # 2056.9 to ~2366
    {'name': 'Аренда', 'x': 2379, 'width': 1320},                      # 2379.4 to ~3699
    {'name': 'Оплата', 'x': 3718, 'width': 730},                       # 3718.3 to ~4448
    {'name': 'Отзывы', 'x': 4463, 'width': 550},                       # 4463.1 to end
]

# Get original viewBox
viewBox = root.get('viewBox').split()
orig_width = float(viewBox[2])
orig_height = float(viewBox[3])

print(f"\nOriginal SVG: {orig_width} x {orig_height}")
print(f"\nCreating {len(regions)} separate SVGs...")

# Create separate SVG for each region
for i, region in enumerate(regions, 1):
    # Create new SVG
    new_svg = ET.Element('svg')
    new_svg.set('version', '1.1')
    new_svg.set('xmlns', 'http://www.w3.org/2000/svg')
    new_svg.set('viewBox', f"0 0 {region['width']} {orig_height}")
    new_svg.set('width', str(region['width'] * 3))
    new_svg.set('height', str(orig_height * 3))
    
    # Copy defs
    defs = root.find('.//{http://www.w3.org/2000/svg}defs')
    if defs is not None:
        new_svg.append(defs)
    
    # Add white background
    bg_rect = ET.SubElement(new_svg, 'rect')
    bg_rect.set('x', '0')
    bg_rect.set('y', '0')
    bg_rect.set('width', str(region['width']))
    bg_rect.set('height', str(orig_height))
    bg_rect.set('fill', '#ffffff')
    
    # Filter and copy elements that are in this region
    for elem in root:
        if elem.tag.endswith('g') or elem.tag.endswith('rect'):
            transform = elem.get('transform', '')
            match = re.search(r'translate\(([\d.]+)', transform)
            if match:
                x = float(match.group(1))
                # Check if element is in this region
                if region['x'] <= x < region['x'] + region['width']:
                    # Clone the element and adjust its transform
                    new_elem = ET.fromstring(ET.tostring(elem))
                    # Adjust x coordinate in the transform
                    new_x = x - region['x']
                    new_transform = re.sub(
                        r'translate\(([\d.]+)',
                        f'translate({new_x}',
                        transform
                    )
                    new_elem.set('transform', new_transform)
                    new_svg.append(new_elem)
            elif 'stroke-linecap' in elem.get('stroke-linecap', ''):
                # This might be a stroke element without obvious translate, skip for now
                pass
    
    # Save the new SVG
    filename = f"microservice_{i}_{region['name'].replace(' ', '_')}.svg"
    new_tree = ET.ElementTree(new_svg)
    ET.indent(new_tree, space='  ')
    new_tree.write(filename, encoding='utf-8', xml_declaration=True)
    print(f"Created: {filename}")

print("\nDone!")