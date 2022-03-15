pragma solidity >=0.5.16;
pragma experimental ABIEncoderV2;

// Record of contact between two or more individuals.
contract Contact {


    event Message(
        string indexed message
    );


    event Pub_Key(
        string indexed pub_key
    );


    event Key_Cipher(
        string indexed key_cipher
    );


    // state variables
	string[] pub_keychain;
	string[] message_log;
    string[] cipher_keychain;




    event msg_received(string message);
    event pub_key_received(string pub_key);
    event key_cipher_received(string key_cipher);

    // messaging functions
    function add_message(string calldata new_message) external {
    	message_log.push(new_message);
    	emit msg_received(new_message);
    }

    function get_message_by_number(uint msg_num) external view returns (string memory) {
        return message_log[msg_num];
    }

    function get_message_state() external view returns (uint) {
        return message_log.length;
    }





    // pubkey functions
    function add_pub_key(string calldata new_pub_key) external {
	    pub_keychain.push(new_pub_key);
	    emit pub_key_received(new_pub_key);
    }

    function get_pub_key_by_number(uint pk_num) external view returns (string memory) {
    	return pub_keychain[pk_num];
    }

    function get_pub_key_state() external view returns (uint) {
        return pub_keychain.length;
    }





    // key_cipher functions
    function add_key_cipher(string calldata new_key_cipher) external {
    	cipher_keychain.push(new_key_cipher);
    	emit key_cipher_received(new_key_cipher);
    }

    function get_key_cipher_by_number(uint kc_num) external view returns (string memory) {
 	    return cipher_keychain[kc_num];
    }

    function get_key_cipher_state() external view returns (uint) {
        return cipher_keychain.length;
    }
}
