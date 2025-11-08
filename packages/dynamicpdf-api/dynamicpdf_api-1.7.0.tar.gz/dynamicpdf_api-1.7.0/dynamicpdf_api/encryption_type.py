class EncryptionType:
    '''
    Specifies Encryption Type.
    
    '''
    
    # Represents a RC4 40 bit security.
    RC440 = "rc440"
    
    # Represents a RC4 128 bit security.
    RC4128 = "rc4128"
    
    # Represents a AES 128 bit security with CBC cipher mode.
    Aes128Cbc = "aes128cbc"
    
    # Represents a AES 256 bit security with CBC cipher mode.
    Aes256Cbc = "aes256cbc"
    
    # Represents a No security.
    NONE= "none"