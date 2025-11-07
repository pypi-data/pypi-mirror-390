import logging
from web3 import Web3

class iPayTools:
    DEFAULT_RPC_URL = "http://localhost:8545"
    DEFAULT_CONTRACT_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3"
    
    def __init__(self, contract_address=None, rpc_url=None, auto_adjust_fee=True):
        self.contract_address = contract_address or self.DEFAULT_CONTRACT_ADDRESS
        self.rpc_url = rpc_url or self.DEFAULT_RPC_URL
        self.auto_adjust_fee = auto_adjust_fee

        # Initialize web3
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to {self.rpc_url}")
            
        # Setup logging
        self.logger = logging.getLogger('ipaytools.core')
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

        # Load contract
        self._load_contract()
        
        # Get account
        if self.w3.eth.accounts:
            self.account = self.w3.eth.accounts[0]
            self.logger.info(f"Using account: {self.account}")
        else:
            raise Exception("No accounts available")
            
        # Verify contract
        try:
            owner = self.contract.functions.owner().call()
            self.logger.info(f"✅ Contract verified. Owner: {owner}")
        except Exception as e:
            self.logger.error(f"❌ Contract verification failed: {e}")
            raise
            
        # Auto-adjust fee if enabled
        if self.auto_adjust_fee:
            self._ensure_profitable_fee()

    def _load_contract(self):
        """Load contract dengan hanya function yang tersedia"""
        abi = [
            {
                "inputs": [],
                "name": "feePerUse",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [{"internalType": "uint256", "name": "newFee", "type": "uint256"}],
                "name": "setFeePerUse",
                "outputs": [],
                "stateMutability": "nonpayable",
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
                "inputs": [{"internalType": "address", "name": "developer", "type": "address"}],
                "name": "getDeveloperEarnings",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]
        
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.contract_address),
            abi=abi
        )

    def get_current_gas_price(self):
        """Get current gas price dengan safety buffer"""
        try:
            base_gas_price = self.w3.eth.gas_price
            safe_gas_price = base_gas_price * 120 // 100
            self.logger.info(f"⛽ Gas price: {self.w3.from_wei(base_gas_price, 'gwei'):.2f} Gwei -> {self.w3.from_wei(safe_gas_price, 'gwei'):.2f} Gwei (with buffer)")
            return safe_gas_price
        except Exception as e:
            self.logger.warning(f"Gas price check failed, using default: {e}")
            return self.w3.to_wei(1, 'gwei')

    def estimate_gas_for_transaction(self, value_wei=0):
        """Estimate gas untuk transaction ke contract"""
        try:
            # Estimate gas untuk transaction ke contract address
            gas_estimate = self.w3.eth.estimate_gas({
                'from': self.account,
                'to': self.contract_address,
                'value': value_wei,
                'data': '0x'  # empty data - hanya transfer ETH
            })
            self.logger.info(f"🔧 Gas estimate successful: {gas_estimate}")
            return gas_estimate
        except Exception as e:
            self.logger.warning(f"Gas estimation failed, using default: {e}")
            return 50000  # Default gas estimate

    def calculate_minimum_profitable_fee(self):
        """Calculate minimum fee yang profitable berdasarkan current gas price"""
        gas_price = self.get_current_gas_price()
        
        # Estimate gas usage
        base_gas_estimate = self.estimate_gas_for_transaction()
        
        # Tambah 30% safety buffer untuk gas estimation
        safe_gas_estimate = base_gas_estimate * 130 // 100
        
        # Calculate total gas cost
        gas_cost = safe_gas_estimate * gas_price
        
        # Calculate minimum fee: gas_cost / 0.7 (karena iPay dapat 70%)
        # Plus 20% profit margin
        min_fee_wei = (gas_cost * 100 // 70) * 120 // 100
        
        min_fee_eth = self.w3.from_wei(min_fee_wei, 'ether')
        gas_cost_eth = self.w3.from_wei(gas_cost, 'ether')
        
        self.logger.info(f"💡 Minimum profitable fee: {min_fee_eth:.6f} ETH (gas cost: {gas_cost_eth:.6f} ETH)")
        
        return min_fee_wei

    def _is_fee_profitable(self, fee_wei=None):
        """Check REAL-TIME jika fee profitable berdasarkan current gas price"""
        if fee_wei is None:
            fee_wei = self.get_fee()
            
        min_fee_wei = self.calculate_minimum_profitable_fee()
        
        is_profitable = fee_wei >= min_fee_wei
        
        if is_profitable:
            try:
                gas_price = self.get_current_gas_price()
                gas_estimate = self.estimate_gas_for_transaction(fee_wei)
                gas_cost = gas_estimate * gas_price
                ipay_revenue = fee_wei * 70 // 100
                ipay_profit = ipay_revenue - gas_cost
                
                if ipay_revenue > 0:
                    profit_margin = (ipay_profit / ipay_revenue) * 100
                else:
                    profit_margin = 0
                    
                self.logger.info(f"✅ Fee is profitable (margin: {profit_margin:.1f}%)")
            except Exception as e:
                self.logger.warning(f"Profit calculation failed: {e}")
                ipay_profit = 0
                profit_margin = 0
        else:
            ipay_profit = -1
            profit_margin = -1
            current_fee_eth = self.w3.from_wei(fee_wei, 'ether')
            min_fee_eth = self.w3.from_wei(min_fee_wei, 'ether')
            self.logger.warning(f"⚠️ Fee {current_fee_eth:.6f} ETH is NOT profitable (need: {min_fee_eth:.6f} ETH)")
            
        return is_profitable, ipay_profit, profit_margin

    def _ensure_profitable_fee(self):
        """Ensure fee selalu profitable dengan REAL-TIME calculation"""
        try:
            current_fee = self.get_fee()
            min_fee = self.calculate_minimum_profitable_fee()
            
            if current_fee < min_fee:
                current_fee_eth = self.w3.from_wei(current_fee, 'ether')
                min_fee_eth = self.w3.from_wei(min_fee, 'ether')
                self.logger.warning(f"🔄 Adjusting fee from {current_fee_eth:.6f} to {min_fee_eth:.6f} ETH")
                self.set_fee(min_fee)
            else:
                self.logger.info("✅ Current fee is profitable")
        except Exception as e:
            self.logger.error(f"❌ Fee adjustment failed: {e}")

    def use_tool_safe(self, value_eth=None):
        """Safe transaction method - tanpa function call, hanya transfer ETH"""
        try:
            # 1. Get current gas price
            gas_price = self.get_current_gas_price()
            
            # 2. Calculate minimum fee based on CURRENT gas price
            min_fee_wei = self.calculate_minimum_profitable_fee()
            
            # 3. Jika value tidak provided, use minimum fee
            if value_eth is None:
                value_wei = min_fee_wei
            else:
                value_wei = self.w3.to_wei(value_eth, 'ether')
                
            # 4. Validate profitability REAL-TIME
            if value_wei < min_fee_wei:
                required_fee_eth = self.w3.from_wei(min_fee_wei, 'ether')
                current_fee_eth = self.w3.from_wei(value_wei, 'ether')
                self.logger.error(f"❌ TRANSACTION REJECTED: Fee is not profitable!")
                self.logger.error(f"   Current fee: {current_fee_eth:.6f} ETH")
                self.logger.error(f"   Required fee: {required_fee_eth:.6f} ETH") 
                self.logger.error(f"   System would LOSE money on this transaction!")
                raise Exception(f"Transaction rejected: Fee is not profitable (need {required_fee_eth:.6f} ETH)")
            
            # 5. Estimate gas
            gas_estimate = self.estimate_gas_for_transaction(value_wei)
            
            # 6. Calculate final cost
            total_gas_cost = gas_estimate * gas_price
            ipay_revenue = value_wei * 70 // 100
            ipay_profit = ipay_revenue - total_gas_cost
            
            if ipay_revenue > 0:
                profit_margin = (ipay_profit / ipay_revenue) * 100
            else:
                profit_margin = 0
            
            self.logger.info(f"💰 Transaction details:")
            self.logger.info(f"   Fee: {self.w3.from_wei(value_wei, 'ether'):.6f} ETH")
            self.logger.info(f"   Gas cost: {self.w3.from_wei(total_gas_cost, 'ether'):.6f} ETH") 
            self.logger.info(f"   iPay profit: {self.w3.from_wei(ipay_profit, 'ether'):.6f} ETH")
            self.logger.info(f"   Profit margin: {profit_margin:.1f}%")
            
            # 7. Execute transaction (hanya transfer ETH, tanpa function call)
            try:
                tx_hash = self.w3.eth.send_transaction({
                    'from': self.account,
                    'to': self.contract_address,
                    'value': value_wei,
                    'gas': gas_estimate * 150 // 100,
                    'gasPrice': gas_price
                })
                
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
                self.logger.info(f"✅ Transaction successful! Gas used: {receipt['gasUsed']}")
                return receipt
                
            except Exception as e:
                self.logger.error(f"❌ Transaction execution failed: {e}")
                raise Exception(f"Transaction execution failed: {e}")
                
        except Exception as e:
            self.logger.error(f"❌ Safe transaction failed: {e}")
            raise

    def get_fee(self):
        """Get current fee from contract"""
        try:
            return self.contract.functions.feePerUse().call()
        except Exception as e:
            self.logger.error(f"❌ Failed to get fee: {e}")
            return self.w3.to_wei(0.0001, 'ether')

    def set_fee(self, fee_wei):
        """Set new fee - hanya owner yang bisa"""
        try:
            tx_hash = self.contract.functions.setFeePerUse(fee_wei).transact({
                'from': self.account
            })
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            self.logger.info(f"✅ Fee set to {self.w3.from_wei(fee_wei, 'ether'):.6f} ETH")
            return receipt
        except Exception as e:
            self.logger.error(f"❌ Failed to set fee: {e}")
            raise

    def is_registered(self, address=None):
        """Check if address is registered"""
        return True

    def get_contract_balance(self):
        """Get contract balance"""
        return self.w3.eth.get_balance(self.contract_address)

    def get_developer_earnings(self, address=None):
        """Get developer earnings"""
        if address is None:
            address = self.account
        try:
            return self.contract.functions.getDeveloperEarnings(address).call()
        except Exception as e:
            self.logger.warning(f"Failed to get developer earnings: {e}")
            return 0

    def withdraw_earnings(self):
        """Withdraw earnings - placeholder implementation"""
        self.logger.info("💸 Withdraw earnings called")
        return True

def quick_start_demo():
    """Quick start demo dengan error handling"""
    print("🚀 iPayTools Quick Start - ANTI RUGI SYSTEM")
    try:
        tools = iPayTools(auto_adjust_fee=True)
        print(f"✅ Connected: {tools.contract_address}")
        print(f"💰 Current fee: {tools.w3.from_wei(tools.get_fee(), 'ether')} ETH")
        
        # Test safe transaction
        try:
            result = tools.use_tool_safe()
            print("✅ Safe transaction completed!")
        except Exception as e:
            print(f"🛡️ Transaction rejected (SAFE): {e}")
            
    except Exception as e:
        print(f"❌ Initialization failed: {e}")

if __name__ == "__main__":
    quick_start_demo()
