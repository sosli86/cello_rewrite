# Cello
## The MVC edition

Infrastructure for encrypted asymmetric key sharing has been added to the model.

The cryptography modules are almost finished being tested. They will entirely replace the database for storing 
membership data for contracts.

## Smart contract
  *cello_mvc/Contact.sol: fully tested and functional but is not scalable. Need to add the functionality to detect when the contract is almost full and create a new daisy-chained contract to store new messages. Event logging functions are included but as yet unutilized by the client.

## Python modules
### Complete and fully tested
  *cello_mvc.CelloDB: database module.
  *cello_mvc.Contract: contract module interfaces with smart contract.
  *cello_mvc.CelloMod.ActiveContract: contract module implementation for the model.
  
### Almost complete and mostly tested
  *cello_mvc.CelloCryptog.ContractKeyring: stores encrypted and unencrypted contract keys and member public keys,
                                            along with functions for encrypting and decrypting contract messages, 
                                            encrypting asymmetric contract keys, and enumerating contract     
                                            membership.
                                          At the moment, we are transitioning to using the ContractKeyring to 
                                            store most of the contract membership data instead of the database.
                                          ** KEY BASE SHOULD BE ENCRYPTED FOR THE FINAL PROTOTYPE.
  *cello_mvc.CelloCryptog.CelloKeyring: stores user private and public keys and decrypts contract key ciphers.

### Previously tested but needs refactoring to account for recent updates
  *cello_mvc.CelloMod.UserMod: the point of contact for the controller and view, extends all of the above modules.
  
### Previously tested but need rewriting
  *cello_mvc.CelloControl: several of the UserMod functions (add message, etc.) should be moved here.
  *cello_mvc.CelloView: the main module prompts the user for user info and contract info, then launches a tkinter-
                        based GUI to update messages from the contract via the model in realtime and allow for
                        user entry of new messages.
