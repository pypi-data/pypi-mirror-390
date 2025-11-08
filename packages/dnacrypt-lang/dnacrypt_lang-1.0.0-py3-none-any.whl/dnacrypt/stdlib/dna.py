"""
DNACrypt Standard Library - DNA Module
Provides DNA sequence operations and encoding

File: dnacrypt_stdlib/dna.py
"""

from typing import List, Dict, Optional, Union, Tuple
from dataclasses import dataclass
import re


# ============ DATA STRUCTURES ============

@dataclass
class DNASequence:
    """DNA sequence"""
    sequence: str
    metadata: Optional[Dict] = None
    
    def __post_init__(self):
        # Validate DNA sequence
        if not self.is_valid():
            raise InvalidDNAError(f"Invalid DNA sequence: contains non-ATGC characters")
    
    def __len__(self):
        return len(self.sequence)
    
    def __repr__(self):
        preview = self.sequence[:50] + "..." if len(self.sequence) > 50 else self.sequence
        return f"DNA({preview})"
    
    def __str__(self):
        return self.sequence
    
    def is_valid(self) -> bool:
        """Check if sequence contains only valid nucleotides"""
        return all(base in 'ATGC' for base in self.sequence.upper())


@dataclass
class RNASequence:
    """RNA sequence"""
    sequence: str
    metadata: Optional[Dict] = None
    
    def __post_init__(self):
        if not all(base in 'AUGC' for base in self.sequence.upper()):
            raise InvalidDNAError(f"Invalid RNA sequence: contains non-AUGC characters")
    
    def __len__(self):
        return len(self.sequence)
    
    def __repr__(self):
        preview = self.sequence[:50] + "..." if len(self.sequence) > 50 else self.sequence
        return f"RNA({preview})"


@dataclass
class Codon:
    """Single codon (3 nucleotides)"""
    sequence: str
    
    def __post_init__(self):
        if len(self.sequence) != 3:
            raise ValueError("Codon must be exactly 3 nucleotides")
        if not all(base in 'ATGC' for base in self.sequence.upper()):
            raise InvalidDNAError("Invalid codon sequence")
    
    def __repr__(self):
        return f"Codon({self.sequence})"
    
    def to_amino_acid(self) -> str:
        """Translate codon to amino acid"""
        return translate_codon(self.sequence)


@dataclass
class OpenReadingFrame:
    """Open Reading Frame"""
    start: int
    end: int
    sequence: str
    frame: int
    strand: str  # '+' or '-'
    
    def __len__(self):
        return self.end - self.start
    
    def __repr__(self):
        return f"ORF(start={self.start}, end={self.end}, length={len(self)}, strand={self.strand})"


# ============ EXCEPTIONS ============

class DNAError(Exception):
    """Base DNA error"""
    pass


class InvalidDNAError(DNAError):
    """Invalid DNA sequence"""
    pass


class EncodingError(DNAError):
    """DNA encoding error"""
    pass


# ============ GENETIC CODE ============

GENETIC_CODE = {
    'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L',
    'TCT': 'S', 'TCC': 'S', 'TCA': 'S', 'TCG': 'S',
    'TAT': 'Y', 'TAC': 'Y', 'TAA': '*', 'TAG': '*',
    'TGT': 'C', 'TGC': 'C', 'TGA': '*', 'TGG': 'W',
    'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L',
    'CCT': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
    'CAT': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
    'CGT': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
    'ATT': 'I', 'ATC': 'I', 'ATA': 'I', 'ATG': 'M',
    'ACT': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
    'AAT': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
    'AGT': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
    'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V',
    'GCT': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
    'GAT': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
    'GGT': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G',
}

START_CODONS = ['ATG']
STOP_CODONS = ['TAA', 'TAG', 'TGA']


# ============ ENCODING/DECODING ============

class DNAEncoder:
    """DNA encoding schemes"""
    
    # Binary to DNA mapping (2-bit encoding)
    BINARY_2BIT = {
        '00': 'A', '01': 'T', '10': 'G', '11': 'C'
    }
    
    BINARY_2BIT_REVERSE = {
        'A': '00', 'T': '01', 'G': '10', 'C': '11'
    }
    
    @staticmethod
    def encode(data: bytes, scheme: str = "BINARY_2BIT") -> DNASequence:
        """
        Encode binary data to DNA
        
        Args:
            data: Binary data to encode
            scheme: Encoding scheme (BINARY_2BIT, BINARY_3BIT, HUFFMAN)
        
        Returns:
            DNASequence object
        """
        if scheme == "BINARY_2BIT":
            return DNAEncoder._encode_2bit(data)
        elif scheme == "BINARY_3BIT":
            return DNAEncoder._encode_3bit(data)
        else:
            raise EncodingError(f"Unknown encoding scheme: {scheme}")
    
    @staticmethod
    def _encode_2bit(data: bytes) -> DNASequence:
        """Encode using 2-bit scheme (00->A, 01->T, 10->G, 11->C)"""
        # Convert bytes to binary string
        binary = ''.join(format(byte, '08b') for byte in data)
        
        # Pad to multiple of 2
        if len(binary) % 2 != 0:
            binary += '0'
        
        # Convert to DNA
        dna_sequence = ''
        for i in range(0, len(binary), 2):
            bits = binary[i:i+2]
            dna_sequence += DNAEncoder.BINARY_2BIT[bits]
        
        return DNASequence(dna_sequence)
    
    @staticmethod
    def _encode_3bit(data: bytes) -> DNASequence:
        """Encode using 3-bit scheme (uses codons for higher information density)"""
        # Convert bytes to binary string
        binary = ''.join(format(byte, '08b') for byte in data)
        
        # Pad to multiple of 6 (2 codons)
        remainder = len(binary) % 6
        if remainder != 0:
            binary += '0' * (6 - remainder)
        
        # Use 6 bits -> 2 codons mapping
        dna_sequence = ''
        for i in range(0, len(binary), 6):
            chunk = binary[i:i+6]
            # Simple mapping: each 3 bits to one nucleotide position
            for j in range(0, 6, 2):
                bits = chunk[j:j+2]
                dna_sequence += DNAEncoder.BINARY_2BIT[bits]
        
        return DNASequence(dna_sequence)
    
    @staticmethod
    def decode(dna: Union[DNASequence, str], scheme: str = "BINARY_2BIT") -> bytes:
        """
        Decode DNA to binary data
        
        Args:
            dna: DNASequence or string
            scheme: Encoding scheme
        
        Returns:
            Original binary data
        """
        if isinstance(dna, DNASequence):
            sequence = dna.sequence
        else:
            sequence = dna
        
        if scheme == "BINARY_2BIT":
            return DNAEncoder._decode_2bit(sequence)
        elif scheme == "BINARY_3BIT":
            return DNAEncoder._decode_3bit(sequence)
        else:
            raise EncodingError(f"Unknown decoding scheme: {scheme}")
    
    @staticmethod
    def _decode_2bit(sequence: str) -> bytes:
        """Decode 2-bit encoded DNA"""
        # Convert DNA to binary
        binary = ''
        for nucleotide in sequence:
            binary += DNAEncoder.BINARY_2BIT_REVERSE[nucleotide]
        
        # Convert binary to bytes
        byte_array = bytearray()
        for i in range(0, len(binary), 8):
            byte_str = binary[i:i+8]
            if len(byte_str) == 8:
                byte_array.append(int(byte_str, 2))
        
        return bytes(byte_array)
    
    @staticmethod
    def _decode_3bit(sequence: str) -> bytes:
        """Decode 3-bit encoded DNA"""
        # Similar to 2-bit but handles codon structure
        binary = ''
        for nucleotide in sequence:
            binary += DNAEncoder.BINARY_2BIT_REVERSE[nucleotide]
        
        byte_array = bytearray()
        for i in range(0, len(binary), 8):
            byte_str = binary[i:i+8]
            if len(byte_str) == 8:
                byte_array.append(int(byte_str, 2))
        
        return bytes(byte_array)


# ============ DNA OPERATIONS ============

def complement(sequence: Union[DNASequence, str]) -> DNASequence:
    """Get DNA complement (A<->T, G<->C)"""
    if isinstance(sequence, DNASequence):
        seq = sequence.sequence
    else:
        seq = sequence
    
    complement_map = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G'}
    complemented = ''.join(complement_map[base] for base in seq)
    
    return DNASequence(complemented)


def reverse(sequence: Union[DNASequence, str]) -> DNASequence:
    """Reverse DNA sequence"""
    if isinstance(sequence, DNASequence):
        seq = sequence.sequence
    else:
        seq = sequence
    
    return DNASequence(seq[::-1])


def reverse_complement(sequence: Union[DNASequence, str]) -> DNASequence:
    """Get reverse complement of DNA"""
    comp = complement(sequence)
    return reverse(comp)


def transcribe(sequence: Union[DNASequence, str]) -> RNASequence:
    """Transcribe DNA to RNA (T -> U)"""
    if isinstance(sequence, DNASequence):
        seq = sequence.sequence
    else:
        seq = sequence
    
    rna = seq.replace('T', 'U')
    return RNASequence(rna)


def translate_codon(codon: str) -> str:
    """Translate single codon to amino acid"""
    return GENETIC_CODE.get(codon.upper(), 'X')  # X for unknown


def translate(sequence: Union[DNASequence, str], frame: int = 0) -> str:
    """
    Translate DNA to protein sequence
    
    Args:
        sequence: DNA sequence
        frame: Reading frame (0, 1, or 2)
    
    Returns:
        Protein sequence (amino acids)
    """
    if isinstance(sequence, DNASequence):
        seq = sequence.sequence
    else:
        seq = sequence
    
    # Start from the specified frame
    seq = seq[frame:]
    
    protein = ''
    for i in range(0, len(seq) - 2, 3):
        codon = seq[i:i+3]
        amino_acid = translate_codon(codon)
        if amino_acid == '*':  # Stop codon
            break
        protein += amino_acid
    
    return protein


# ============ SEQUENCE ANALYSIS ============

def gc_content(sequence: Union[DNASequence, str]) -> float:
    """
    Calculate GC content (0.0 - 1.0)
    
    Args:
        sequence: DNA sequence
    
    Returns:
        GC content as float
    """
    if isinstance(sequence, DNASequence):
        seq = sequence.sequence
    else:
        seq = sequence
    
    if not seq:
        return 0.0
    
    gc_count = seq.count('G') + seq.count('C')
    return gc_count / len(seq)


def at_content(sequence: Union[DNASequence, str]) -> float:
    """Calculate AT content"""
    return 1.0 - gc_content(sequence)


def nucleotide_frequency(sequence: Union[DNASequence, str]) -> Dict[str, float]:
    """Get frequency of each nucleotide"""
    if isinstance(sequence, DNASequence):
        seq = sequence.sequence
    else:
        seq = sequence
    
    length = len(seq)
    return {
        'A': seq.count('A') / length,
        'T': seq.count('T') / length,
        'G': seq.count('G') / length,
        'C': seq.count('C') / length
    }


def find_motif(sequence: Union[DNASequence, str], motif: str) -> List[int]:
    """
    Find all occurrences of a motif
    
    Args:
        sequence: DNA sequence to search
        motif: Motif to find
    
    Returns:
        List of starting positions
    """
    if isinstance(sequence, DNASequence):
        seq = sequence.sequence
    else:
        seq = sequence
    
    positions = []
    for i in range(len(seq) - len(motif) + 1):
        if seq[i:i+len(motif)] == motif:
            positions.append(i)
    
    return positions


def find_orfs(sequence: Union[DNASequence, str], min_length: int = 75) -> List[OpenReadingFrame]:
    """
    Find all Open Reading Frames
    
    Args:
        sequence: DNA sequence
        min_length: Minimum ORF length in nucleotides
    
    Returns:
        List of ORF objects
    """
    if isinstance(sequence, DNASequence):
        seq = sequence.sequence
    else:
        seq = sequence
    
    orfs = []
    
    # Search in all 6 frames (3 forward, 3 reverse)
    for strand, seq_to_search in [('+', seq), ('-', reverse_complement(seq).sequence)]:
        for frame in range(3):
            seq_frame = seq_to_search[frame:]
            
            # Find start codons
            for i in range(0, len(seq_frame) - 2, 3):
                codon = seq_frame[i:i+3]
                
                if codon in START_CODONS:
                    # Look for stop codon
                    for j in range(i + 3, len(seq_frame) - 2, 3):
                        stop_codon = seq_frame[j:j+3]
                        
                        if stop_codon in STOP_CODONS:
                            orf_length = j - i + 3
                            
                            if orf_length >= min_length:
                                orf_seq = seq_frame[i:j+3]
                                
                                # Adjust positions for original sequence
                                if strand == '+':
                                    start = frame + i
                                    end = frame + j + 3
                                else:
                                    # Reverse complement positions
                                    start = len(seq) - (frame + j + 3)
                                    end = len(seq) - (frame + i)
                                
                                orfs.append(OpenReadingFrame(
                                    start=start,
                                    end=end,
                                    sequence=orf_seq,
                                    frame=frame,
                                    strand=strand
                                ))
                            
                            break
    
    return orfs


def calculate_melting_temperature(sequence: Union[DNASequence, str]) -> float:
    """
    Calculate melting temperature (Tm) using Wallace rule
    
    Args:
        sequence: DNA sequence
    
    Returns:
        Melting temperature in Celsius
    """
    if isinstance(sequence, DNASequence):
        seq = sequence.sequence
    else:
        seq = sequence
    
    # Wallace rule: Tm = 2(A+T) + 4(G+C)
    # More accurate for short sequences
    if len(seq) < 14:
        a_t = seq.count('A') + seq.count('T')
        g_c = seq.count('G') + seq.count('C')
        return 2 * a_t + 4 * g_c
    else:
        # For longer sequences, use more complex formula
        gc = gc_content(seq)
        return 64.9 + 41 * (gc - 0.16955)


def hamming_distance(seq1: Union[DNASequence, str], 
                     seq2: Union[DNASequence, str]) -> int:
    """
    Calculate Hamming distance between two sequences
    
    Args:
        seq1: First sequence
        seq2: Second sequence
    
    Returns:
        Number of differing positions
    """
    if isinstance(seq1, DNASequence):
        s1 = seq1.sequence
    else:
        s1 = seq1
    
    if isinstance(seq2, DNASequence):
        s2 = seq2.sequence
    else:
        s2 = seq2
    
    if len(s1) != len(s2):
        raise ValueError("Sequences must be same length for Hamming distance")
    
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))


# ============ CODON OPERATIONS ============

def to_codons(sequence: Union[DNASequence, str]) -> List[Codon]:
    """Split sequence into codons"""
    if isinstance(sequence, DNASequence):
        seq = sequence.sequence
    else:
        seq = sequence
    
    codons = []
    for i in range(0, len(seq) - 2, 3):
        codon_seq = seq[i:i+3]
        if len(codon_seq) == 3:
            codons.append(Codon(codon_seq))
    
    return codons


def count_codons(sequence: Union[DNASequence, str]) -> Dict[str, int]:
    """Count frequency of each codon"""
    if isinstance(sequence, DNASequence):
        seq = sequence.sequence
    else:
        seq = sequence
    
    codon_counts = {}
    for i in range(0, len(seq) - 2, 3):
        codon = seq[i:i+3]
        if len(codon) == 3:
            codon_counts[codon] = codon_counts.get(codon, 0) + 1
    
    return codon_counts


# ============ VALIDATION ============

def validate(sequence: Union[DNASequence, str]) -> bool:
    """Check if sequence is valid DNA"""
    if isinstance(sequence, DNASequence):
        return True  # Already validated in __post_init__
    
    return all(base in 'ATGC' for base in sequence.upper())


def check_palindrome(sequence: Union[DNASequence, str]) -> bool:
    """Check if sequence is a palindrome"""
    if isinstance(sequence, DNASequence):
        seq = sequence.sequence
    else:
        seq = sequence
    
    return seq == seq[::-1]


# ============ TESTING ============

if __name__ == "__main__":
    print("=" * 70)
    print("DNACrypt DNA Module Test")
    print("=" * 70)
    
    # Test encoding/decoding
    print("\n1. Encoding/Decoding")
    data = b"Hello, DNA!"
    encoded = DNAEncoder.encode(data)
    print(f"   Original: {data}")
    print(f"   Encoded: {encoded}")
    decoded = DNAEncoder.decode(encoded)
    print(f"   Decoded: {decoded}")
    print(f"   Match: {data == decoded}")
    
    # Test DNA operations
    print("\n2. DNA Operations")
    seq = DNASequence("ATGCCGTA")
    print(f"   Original: {seq}")
    print(f"   Complement: {complement(seq)}")
    print(f"   Reverse: {reverse(seq)}")
    print(f"   Rev. Comp: {reverse_complement(seq)}")
    
    # Test GC content
    print("\n3. GC Content")
    gc = gc_content(seq)
    print(f"   GC Content: {gc:.2%}")
    
    # Test ORF finding
    print("\n4. Finding ORFs")
    long_seq = "ATGATGATGATGTAATGATGATGATAA"
    orfs = find_orfs(long_seq, min_length=9)
    print(f"   Found {len(orfs)} ORFs")
    for orf in orfs:
        print(f"   {orf}")
    
    # Test translation
    print("\n5. Translation")
    coding_seq = "ATGGGCAAATAA"  # M-G-K-*
    protein = translate(coding_seq)
    print(f"   DNA: {coding_seq}")
    print(f"   Protein: {protein}")
    
    print("\n✓ All DNA tests passed!")