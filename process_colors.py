import pandas as pd

def get_base_color(detailed_color):
    """Categorizes a detailed color name into a base color."""
    color_lower = detailed_color.strip().lower()

    # Priority order matters here
    if 'pink' in color_lower or 'blush' in color_lower or 'rose' in color_lower:
        return 'Pink'
    if 'red' in color_lower or 'terracotta' in color_lower:
        return 'Red'
    if 'green' in color_lower or 'sage' in color_lower or 'moss' in color_lower or 'eucalyptus' in color_lower or 'olive' in color_lower or 'teal' in color_lower or 'sea glass' in color_lower:
        return 'Green'
    if 'blue' in color_lower or 'indigo' in color_lower or 'sapphire' in color_lower or 'sky' in color_lower or 'coastal' in color_lower or 'slate' in color_lower:
        return 'Blue'
    if 'brown' in color_lower or 'driftwood' in color_lower or 'clay' in color_lower:
        return 'Brown'
    if 'black' in color_lower:
        return 'Black'
    if 'white' in color_lower or 'snow' in color_lower or 'ivory' in color_lower:
        return 'White'
    if 'grey' in color_lower or 'gray' in color_lower or 'charcoal' in color_lower or 'stone' in color_lower or 'fog' in color_lower or 'dove' in color_lower or 'storm' in color_lower or 'silver' in color_lower or 'pearl' in color_lower:
        return 'Grey'
    if 'beige' in color_lower or 'sand' in color_lower or 'cream' in color_lower or 'oat' in color_lower or 'dune' in color_lower or 'taupe' in color_lower:
        return 'Beige'
    if 'fig' in color_lower:
        return 'Purple'
    if 'butter' in color_lower:
        return 'Yellow'
    if 'stripe' in color_lower:
        return 'Pattern'
    
    # Default to the original name if no category is found
    return detailed_color.strip()

def main():
    """
    Reads raw color data, categorizes it, and saves it to an Excel file.
    """
    try:
        # Read the raw data from the text file
        with open('colors_raw.txt', 'r', encoding='utf-8') as f:
            original_colors = f.readlines()

        processed_data = []
        for color in original_colors:
            color_stripped = color.strip()
            if color_stripped:  # Ensure not an empty line
                base_color = get_base_color(color_stripped)
                processed_data.append([color_stripped, base_color])

        # Create a pandas DataFrame
        df = pd.DataFrame(processed_data, columns=['Исходное название', 'Базовый цвет'])

        # Define the output filename
        output_filename = 'colors_processed.xlsx'

        # Save the DataFrame to an Excel file, without the pandas index
        df.to_excel(output_filename, index=False)

        print(f"Файл '{output_filename}' успешно создан!")
        print("Он содержит ваши данные в двух отдельных столбцах.")

    except FileNotFoundError:
        print("Ошибка: Файл 'colors_raw.txt' не найден. Убедитесь, что он находится в той же папке, что и скрипт.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    main()
