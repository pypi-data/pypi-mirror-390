"""
iPayTools Core Module - Fixed Version
"""
import os
import json
from web3 import Web3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class iPayTools:
    DEFAULT_CONTRACT_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3"
    DEFAULT_RPC_URL = "http://localhost:8545"

    def __init__(self, contract_address=None, rpc_url=None):
        # Contract address yang baru
        self.contract_address = contract_address or self.DEFAULT_CONTRACT_ADDRESS
        self.rpc_url = rpc_url or self.DEFAULT_RPC_URL

        # Initialize web3
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to {self.rpc_url}")

        # Set default account (first account from hardhat)
        self.account = self.w3.eth.accounts[0] if self.w3.eth.accounts else None
        if self.account:
            logger.info(f"Using account: {self.account}")

        # Load contract
        self.contract = self._load_contract()

    def _load_contract(self):
        """Load contract dengan ABI yang benar"""
        try:
            # ABI yang sesuai dengan kontrak deployed
            abi = [
                # ✅ registerApp TANPA PARAMETER & NONPAYABLE
                {
                    "inputs": [],
                    "name": "registerApp",
                    "outputs": [],
                    "stateMutability": "nonpayable",  # ✅ TIDAK BUTUH ETH
                    "type": "function"
                },
                {
                    "inputs": [{"internalType": "address", "name": "", "type": "address"}],
                    "name": "registeredApps",
                    "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                    "stateMutability": "view",
                    "type": "function"
                },
                {
                    "inputs": [],
                    "name": "feePerUse",
                    "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                    "stateMutability": "view",
                    "type": "function"
                },
                {
                    "inputs": [],
                    "name": "owner",
                    "outputs": [{"internalType": "address", "name": "", "type": "address"}],
                    "stateMutability": "view",
                    "type": "function"
                },
                {
                    "inputs": [],
                    "name": "getContractBalance",
                    "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                    "stateMutability": "view",
                    "type": "function"
                },
                {
                    "inputs": [{"internalType": "address", "name": "_developer", "type": "address"}],
                    "name": "getDeveloperEarnings",
                    "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                    "stateMutability": "view",
                    "type": "function"
                },
                {
                    "inputs": [{"internalType": "address", "name": "", "type": "address"}],
                    "name": "developerEarnings",
                    "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                    "stateMutability": "view",
                    "type": "function"
                },
                {
                    "inputs": [],
                    "name": "totalEarnings",
                    "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                    "stateMutability": "view",
                    "type": "function"
                },
                {
                    "inputs": [],
                    "name": "totalTransactions",
                    "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                    "stateMutability": "view",
                    "type": "function"
                },
                {
                    "inputs": [{"internalType": "uint256", "name": "_fee", "type": "uint256"}],
                    "name": "setFeePerUse",
                    "outputs": [],
                    "stateMutability": "nonpayable",
                    "type": "function"
                },
                {
                    "inputs": [],
                    "name": "useTool",
                    "outputs": [],
                    "stateMutability": "payable",  # ✅ BUTUH ETH
                    "type": "function"
                },
                {
                    "inputs": [],
                    "name": "withdrawEarnings",
                    "outputs": [],
                    "stateMutability": "nonpayable",
                    "type": "function"
                },
                {
                    "inputs": [],
                    "name": "withdrawOwnerEarnings",
                    "outputs": [],
                    "stateMutability": "nonpayable",
                    "type": "function"
                }
            ]

            contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.contract_address),
                abi=abi
            )

            # Verify contract is accessible
            try:
                owner = contract.functions.owner().call()
                logger.info(f"✅ Contract verified. Owner: {owner}")
                return contract
            except Exception as e:
                logger.error(f"❌ Contract verification failed: {e}")
                raise

        except Exception as e:
            logger.error(f"❌ Contract loading failed: {e}")
            raise

    def is_registered(self, address=None):
        """Check if address is registered"""
        check_address = address or self.account
        if not check_address:
            raise Exception("No address provided for check")

        try:
            is_registered = self.contract.functions.registeredApps(
                Web3.to_checksum_address(check_address)
            ).call()
            logger.info(f"📋 Registration check for {check_address}: {is_registered}")
            return is_registered
        except Exception as e:
            logger.error(f"❌ Registration check failed: {e}")
            return False

    def register_app(self, app_name=None):
        """Register an application - GRATIS tidak butuh bayar"""
        if not self.account:
            raise Exception("No account available for registration")

        try:
            # Check if already registered
            if self.is_registered():
                logger.info("✅ Already registered")
                return True

            # Build transaction - TANPA VALUE sama sekali
            transaction = {
                'from': self.account,
                'gas': 100000,  # Reduced gas
                'gasPrice': self.w3.eth.gas_price
            }

            logger.info("🔄 Sending registration transaction...")

            # Send transaction - ✅ TANPA PARAMETER & TANPA VALUE
            tx_hash = self.contract.functions.registerApp().transact(transaction)

            logger.info(f"⏳ Waiting for transaction: {tx_hash.hex()}")

            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                logger.info(f"✅ Registration successful! Tx: {tx_hash.hex()}")
                logger.info(f"📊 Gas used: {receipt.gasUsed}")
                return True
            else:
                logger.error(f"❌ Registration failed. Tx: {tx_hash.hex()}")
                return False

        except Exception as e:
            logger.error(f"❌ Registration failed: {e}")
            raise Exception(f"Failed to register app: {e}")

    def get_fee(self):
        """Get current fee amount in ETH"""
        try:
            fee_wei = self.contract.functions.feePerUse().call()
            fee_eth = self.w3.from_wei(fee_wei, 'ether')
            return fee_eth
        except Exception as e:
            logger.error(f"❌ Get fee failed: {e}")
            return 0

    def get_contract_balance(self):
        """Get contract balance in ETH"""
        try:
            balance_wei = self.contract.functions.getContractBalance().call()
            balance_eth = self.w3.from_wei(balance_wei, 'ether')
            return balance_eth
        except Exception as e:
            logger.error(f"❌ Get contract balance failed: {e}")
            return 0

    def get_developer_earnings(self, address=None):
        """Get developer earnings in ETH"""
        check_address = address or self.account
        if not check_address:
            raise Exception("No address provided")

        try:
            earnings_wei = self.contract.functions.getDeveloperEarnings(
                Web3.to_checksum_address(check_address)
            ).call()
            earnings_eth = self.w3.from_wei(earnings_wei, 'ether')
            return earnings_eth
        except Exception as e:
            logger.error(f"❌ Get developer earnings failed: {e}")
            return 0

    def use_tool(self, value_eth=0.0001):
        """Use a tool (pay fee)"""
        if not self.account:
            raise Exception("No account available")

        try:
            value_wei = self.w3.to_wei(value_eth, 'ether')
            
            transaction = {
                'from': self.account,
                'value': value_wei,  # ✅ Hanya useTool yang butuh value
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price
            }

            tx_hash = self.contract.functions.useTool().transact(transaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return receipt.status == 1
            
        except Exception as e:
            logger.error(f"❌ Use tool failed: {e}")
            return False

    def withdraw_earnings(self):
        """Withdraw developer earnings"""
        if not self.account:
            raise Exception("No account available")

        try:
            transaction = {
                'from': self.account,
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price
            }

            tx_hash = self.contract.functions.withdrawEarnings().transact(transaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return receipt.status == 1
            
        except Exception as e:
            logger.error(f"❌ Withdraw earnings failed: {e}")
            return False

# Demo function
def quick_start_demo():
    """Quick start demo function"""
    print("🚀 iPayTools Quick Start Demo")
    print("=" * 40)

    try:
        # 1. Initialize
        print("1. 🔧 Initializing iPayTools...")
        tools = iPayTools()
        print(f"   ✅ Connected to: {tools.rpc_url}")
        print(f"   ✅ Account: {tools.account}")
        print(f"   ✅ Contract: {tools.contract_address}")

        # 2. Test basic functions
        print("\n2. 📊 Testing contract functions...")
        fee = tools.get_fee()
        owner = tools.contract.functions.owner().call()
        balance = tools.get_contract_balance()
        
        print(f"   ✅ Fee per use: {fee} ETH")
        print(f"   ✅ Contract owner: {owner}")
        print(f"   ✅ Contract balance: {balance} ETH")

        # 3. Check registration
        print("\n3. 📝 Checking registration status...")
        is_reg = tools.is_registered()
        print(f"   ✅ Registered: {is_reg}")

        if not is_reg:
            print("   🔄 Registering app...")
            success = tools.register_app("MyAwesomeApp")
            if success:
                print("   ✅ Registration successful!")
                
                # Verify registration
                is_reg_after = tools.is_registered()
                print(f"   ✅ Registration verified: {is_reg_after}")
                
                # Check earnings after registration
                earnings = tools.get_developer_earnings()
                print(f"   💰 Developer earnings: {earnings} ETH")
            else:
                print("   ❌ Registration failed")
        else:
            print("   ℹ️ Already registered!")

        print("\n🎉 Demo completed successfully!")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    quick_start_demo()
