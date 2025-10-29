import sys
from collections import Counter
import struct
import pickle
import gzip

# FanoCoder class to handle encoding and decoding using the Fano algorithm.
class FanoCoder:
    def __init__(self):
        self.codes = {}  # Dictionary to store the character codes.
    
    # Recursive method to build the Fano codes.
    def buildFanoCodes(self, symbols, current_code=""):
        # Base case: If there's only one symbol, assign the code to it.
        if len(symbols) == 1:
            char, _ = symbols[0]
            self.codes[char] = current_code  # Assign the code to the character.
            return
        
        # Finding the optimal point to divide the symbols into two groups.
        total_freq = sum(freq for _, freq in symbols)  # Total frequency of all symbols.
        half = total_freq / 2  # Half the total frequency (ideal split point).
        
        min_diff = float('inf')  # To track the minimal difference in frequency sums.
        split_index = 0  # Index where the symbols should be split.
        left_sum = 0  # Left sum of frequencies.
        
        # Loop to find the best split point to minimize the difference.
        for i in range(1, len(symbols)):
            left_sum += symbols[i-1][1]
            diff = abs(2 * left_sum - total_freq)  # Difference from ideal split.
            if diff < min_diff:
                min_diff = diff
                split_index = i
        
        # Divide the symbols into two groups based on the optimal split index.
        group1 = symbols[:split_index]  # Left group of symbols.
        group2 = symbols[split_index:]  # Right group of symbols.

        # Recursively build codes for both groups.
        self.buildFanoCodes(group1, current_code + "0")  # Add "0" for the left group.
        self.buildFanoCodes(group2, current_code + "1")  # Add "1" for the right group.
    
    # Method to encode a text using the Fano algorithm.
    def encode(self, text):
        if not text:  # If the text is empty, return an empty string.
            return ""
        
        # Count frequency of each character in the text.
        freq = Counter(text)
        # Sort the characters by frequency in descending order.
        symbols = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        
        self.codes = {}  # Reset the codes dictionary.
        self.buildFanoCodes(symbols, "")  # Build the Fano codes for the sorted symbols.
        
        # Encode the text by replacing each character with its corresponding code.
        encoded_text = ''.join(self.codes[char] for char in text)
        return encoded_text
    
    # Method to decode an encoded text using the Fano codes.
    def decode(self, encoded_text):
        if not encoded_text:  # If the encoded text is empty, return an empty string.
            return ""
        
        # Reverse the codes dictionary for decoding.
        reverse_codes = {code: char for char, code in self.codes.items()}
        
        current_code = ""  # Temporary variable to hold the current code being processed.
        decoded_text = ""  # String to store the decoded text.
        
        # Iterate through the encoded text and decode each symbol.
        for bit in encoded_text:
            current_code += bit  # Build the current code bit by bit.
            if current_code in reverse_codes:  # If the current code matches a symbol.
                decoded_text += reverse_codes[current_code]  # Add the decoded symbol.
                current_code = ""  # Reset the current code for the next symbol.
        
        return decoded_text
    
    # Method to print the table of Fano codes, frequencies, and code lengths.
    def printCodesTable(self, text):
        if not self.codes:  # If codes are not assigned, print a warning message.
            print("Codes have not been assigned yet.")
            return
        
        # Count frequencies of characters in the input text.
        freq = Counter(text)
        
        print("\n" + "="*60)
        print("FANO CODES SYMBOLS TABLE")
        print("="*60)
        print("Symbol | Frequency | Fano Code  | Code Length")
        print("-"*60)
        
        # Sort symbols by frequency in descending order.
        sorted_symbols = sorted(self.codes.items(), 
                              key=lambda x: freq[x[0]], 
                              reverse=True)
        
        # Display symbols and their Fano codes.
        for char, code in sorted_symbols:
            # Handle special characters for display.
            if char == ' ':
                char_display = "['']"  # Display a space as [''].
            elif char == '\n':
                char_display = "[/n]"  # Display newline as [newline].
            elif char == '\t':
                char_display = "[tab]"  # Display tab as [tab].
            else:
                char_display = char  # Otherwise, just display the character.
            
            frequency = freq[char]  # Get the frequency of the character.
            code_length = len(code)  # Get the length of the Fano code.
            print(f"{char_display:6} | {frequency:7} | {code:10} | {code_length:5}")
        
        print("-"*60)
        
        total_chars = len(text)  # Total number of characters in the text.
        total_bits = sum(freq[char] * len(self.codes[char]) for char in self.codes.keys())  # Total number of bits after encoding.
        avg_bits_per_char = total_bits / total_chars if total_chars > 0 else 0  # Average number of bits per character.
        
        # Display statistics.
        print(f"Total characters: {total_chars}")
        print(f"Total bits: {total_bits}")
        print(f"Average code length: {avg_bits_per_char:.2f} bits/char")
        print(f"Compression vs ASCII (8 bits): {(1 - avg_bits_per_char/8)*100:.1f}%")

# Convert bit string to bytes
def bits_to_bytes(bit_string):
    # Pad the bit string to make its length multiple of 8
    padding_length = (8 - len(bit_string) % 8) % 8
    padded_bits = bit_string + '0' * padding_length
    
    # Convert to bytes
    bytes_data = bytearray()
    for i in range(0, len(padded_bits), 8):
        byte = padded_bits[i:i+8]
        bytes_data.append(int(byte, 2))
    
    return bytes_data, padding_length

# Convert bytes back to bit string
def bytes_to_bits(bytes_data, padding_length):
    bit_string = ''
    for byte in bytes_data:
        bit_string += format(byte, '08b')
    
    # Remove padding
    if padding_length > 0:
        bit_string = bit_string[:-padding_length]
    
    return bit_string

# Optimized codes serialization
def serialize_codes(codes):
    # Convert codes to more compact format: char(4 bytes) + code_length(1 byte) + code
    serialized = bytearray()
    for char, code in codes.items():
        # Store character as 4-byte Unicode
        serialized.extend(struct.pack('I', ord(char)))
        # Store code length
        serialized.append(len(code))
        # Convert code to bytes (each bit becomes one bit in byte)
        code_bytes, _ = bits_to_bytes(code)
        serialized.extend(code_bytes)
    
    return serialized

def deserialize_codes(serialized_data):
    codes = {}
    index = 0
    while index < len(serialized_data):
        # Read character (4 bytes)
        if index + 4 > len(serialized_data):
            break
        char_code = struct.unpack('I', serialized_data[index:index+4])[0]
        index += 4
        
        # Read code length (1 byte)
        if index >= len(serialized_data):
            break
        code_length = serialized_data[index]
        index += 1
        
        # Calculate how many bytes needed for the code
        code_bytes_needed = (code_length + 7) // 8
        if index + code_bytes_needed > len(serialized_data):
            break
        
        # Read code bytes and convert back to bit string
        code_bytes = serialized_data[index:index + code_bytes_needed]
        code_bit_string = bytes_to_bits(code_bytes, (8 - code_length % 8) % 8)
        code_bit_string = code_bit_string[:code_length]  # Trim to exact length
        
        codes[chr(char_code)] = code_bit_string
        index += code_bytes_needed
    
    return codes

# Function to save encoded data to a binary file with compression.
def saveEncodedToFile(filename, codes, encoded_bits):
    # Convert encoded bits to bytes
    encoded_bytes, padding_length = bits_to_bytes(encoded_bits)
    
    # Serialize codes in compact binary format
    serialized_codes = serialize_codes(codes)
    
    # Write to binary file with compression
    with gzip.open(filename, 'wb') as f:
        # Write codes length (4 bytes)
        f.write(struct.pack('I', len(serialized_codes)))
        # Write serialized codes
        f.write(serialized_codes)
        # Write padding length (1 byte)
        f.write(struct.pack('B', padding_length))
        # Write encoded data length (4 bytes)
        f.write(struct.pack('I', len(encoded_bytes)))
        # Write encoded data
        f.write(encoded_bytes)

# Function to read encoded data from a compressed binary file.
def readEncodedFromFile(filename):
    with gzip.open(filename, 'rb') as f:
        # Read codes length
        codes_length = struct.unpack('I', f.read(4))[0]
        # Read serialized codes
        serialized_codes = f.read(codes_length)
        # Read padding length
        padding_length = struct.unpack('B', f.read(1))[0]
        # Read encoded data length
        data_length = struct.unpack('I', f.read(4))[0]
        # Read encoded data
        encoded_bytes = f.read(data_length)
    
    # Deserialize codes
    codes = deserialize_codes(serialized_codes)
    
    # Convert bytes back to bits
    encoded_bits = bytes_to_bits(encoded_bytes, padding_length)
    
    return codes, encoded_bits

# Function to save decoded data to a file.
def saveDecodedToFile(filename, text):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(text)

# Function to read text from a file.
def readFromFile(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

# Main function to drive the program based on command-line arguments.
def main():
    # If not enough arguments are passed, print usage instructions.
    if len(sys.argv) < 4:
        print("  To encode: python <filename>.py encode input.txt encoded.bin")
        print("  To decode: python <filename>.py decode encoded.bin decoded.txt")
        print("  Note: Output files will have .bin extension for binary format")
        return
    
    command = sys.argv[1]  # The operation (encode or decode).
    input_file = sys.argv[2]  # Input file.
    output_file = sys.argv[3]  # Output file.
    
    coder = FanoCoder()  # Instantiate the FanoCoder.
    
    try:
        if command == "encode":
            # Read the input text file.
            text = readFromFile(input_file)
            
            # Get original file size
            import os
            original_size = os.path.getsize(input_file)
            
            # Encode the text using the FanoCoder.
            encoded_bits = coder.encode(text)
            
            # Save to compressed binary file
            saveEncodedToFile(output_file, coder.codes, encoded_bits)
            
            # Get compressed file size
            compressed_size = os.path.getsize(output_file)
            
            print(f"✅ File '{input_file}' has been encoded to '{output_file}'")
            print(f"Original size: {original_size} bytes")
            print(f"Compressed size: {compressed_size} bytes")
            print(f"Compression ratio: {compressed_size/original_size*100:.1f}%")
            print(f"Space saving: {(1 - compressed_size/original_size)*100:.1f}%")
            print(f"Number of characters: {len(text)}")
            print(f"Encoded size: {len(encoded_bits)} bits ({len(encoded_bits)//8} bytes)")
            
            # Print the Fano codes table.
            coder.printCodesTable(text)
            
        elif command == "decode":
            # Read the encoded binary file.
            codes, encoded_bits = readEncodedFromFile(input_file)
            
            # Set the codes in decoder
            coder.codes = codes
            
            # Decode the encoded bits.
            decoded_text = coder.decode(encoded_bits)
            saveDecodedToFile(output_file, decoded_text)
            
            print(f"✅ File '{input_file}' has been decoded to '{output_file}'")
            print(f"Decoded characters: {len(decoded_text)}")
            
            # Calculate frequencies of characters in the decoded text.
            freq = Counter(decoded_text)
            print("\n" + "="*60)
            print("FANO CODES SYMBOLS TABLE")
            print("="*60)
            print("Symbol | Frequency | Fano Code  | Code Length")
            print("-"*60)
            
            # Display the Fano codes table for the decoded text.
            sorted_symbols = sorted(coder.codes.items(), 
                                  key=lambda x: freq.get(x[0], 0), 
                                  reverse=True)
            
            for char, code in sorted_symbols:
                if char == ' ':
                    char_display = "['']"
                elif char == '\n':
                    char_display = "[/n]"
                elif char == '\t':
                    char_display = "[tab]"
                else:
                    char_display = char
                
                frequency = freq.get(char, 0)
                code_length = len(code)
                print(f"{char_display:6} | {frequency:7} | {code:10} | {code_length:5}")
            
            print("-"*60)
            
        else:
            # If an unknown command is passed, print an error message.
            print("❌ Unknown command. Use 'encode' or 'decode'")
            
    except FileNotFoundError:
        # Handle file not found errors.
        print(f"❌ File '{input_file}' not found")
    except Exception as e:
        # Catch any other errors.
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

# This block ensures the main function is executed when the script is run directly.
if __name__ == "__main__":
        main()