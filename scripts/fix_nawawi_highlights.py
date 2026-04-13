import json
import os

def fix_nawawi():
    input_file = "/Users/fahadiqbal/Documents/Latest_Codes/Islamic work/Islamic AI Agent/knowledge_base/data/forty_hadith_nawawi.json"
    output_file = "/Users/fahadiqbal/Documents/Latest_Codes/Islamic work/Islamic AI Agent/knowledge_base/data/40_hadith_nawawi_highlights.txt"
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found")
        return
        
    with open(input_file, 'r') as f:
        data = json.load(f)
        
    highlights = []
    highlights.append("FORTY HADITH OF IMAM NAWAWI — FOUNDATIONAL ISLAMIC TEACHINGS")
    highlights.append("============================================================")
    highlights.append("")
    
    for hadith in data.get('hadiths', []):
        num = hadith.get('hadithnumber')
        text = hadith.get('text')
        
        if num and text:
            highlights.append(f"HADITH #{num}")
            highlights.append(f"TEXT: {text}")
            highlights.append("-" * 20)
            highlights.append("")
            
    with open(output_file, 'w') as f:
        f.write("\n".join(highlights))
    
    print(f"Successfully fixed {output_file}")

if __name__ == "__main__":
    fix_nawawi()
