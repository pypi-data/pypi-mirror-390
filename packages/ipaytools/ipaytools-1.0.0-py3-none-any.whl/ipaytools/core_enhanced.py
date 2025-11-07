"""
Enhanced iPayTools Core dengan Vertical Solutions
"""
import logging
from web3 import Web3
from .brics.payment_gateway import BRICSPaymentGateway
from .currency.real_rates import RealExchangeRateManager
from .banking.transfer import BankTransferManager
from .vertical.education import EducationPaymentManager
from .vertical.ecommerce import EcommercePaymentManager

class iPayToolsEnhanced:
    def __init__(self, contract_address=None, rpc_url=None, auto_adjust_fee=True):
        self.contract_address = contract_address
        self.rpc_url = rpc_url or "http://localhost:8545"
        self.auto_adjust_fee = auto_adjust_fee

        # Initialize web3
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to {self.rpc_url}")
            
        # Setup logging
        self.logger = logging.getLogger('ipaytools.enhanced')
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

        # Initialize all managers
        self._initialize_managers()
        
        # Get account
        if self.w3.eth.accounts:
            self.account = self.w3.eth.accounts[0]
            self.logger.info(f"Using account: {self.account}")
        else:
            raise Exception("No accounts available")
            
        self.logger.info("🚀 iPayTools Enhanced initialized with vertical solutions")

    def _initialize_managers(self):
        """Initialize all business managers"""
        # Core financial managers
        self.brics_gateway = BRICSPaymentGateway(self.w3, self.contract_address)
        self.real_rates = RealExchangeRateManager()
        self.bank_transfer = BankTransferManager()
        
        # Vertical solution managers
        self.education = EducationPaymentManager(self.brics_gateway)
        self.ecommerce = EcommercePaymentManager(self.brics_gateway)
        
    # Education Vertical Methods
    def pay_course_fee(self, course_id, student_id, amount_idr, payment_currency='IDR'):
        """Pay course fee with international support"""
        return self.education.pay_course_fee(course_id, student_id, amount_idr, payment_currency)
        
    def pay_semester_fee(self, student_id, semester, amount_idr, international_currency=None):
        """Pay semester fee"""
        return self.education.pay_semester_fee(student_id, semester, amount_idr, international_currency)
        
    def get_education_pricing(self, course_type, international=False):
        """Get education pricing"""
        return self.education.get_education_pricing(course_type, international)
        
    # E-commerce Vertical Methods
    def process_online_payment(self, order_id, amount_idr, customer_currency='IDR', customer_country='ID'):
        """Process e-commerce payment"""
        return self.ecommerce.process_online_payment(order_id, amount_idr, customer_currency, customer_country)
        
    def process_subscription(self, subscription_id, plan_type, customer_currency='IDR'):
        """Process subscription payment"""
        return self.ecommerce.process_subscription_payment(subscription_id, plan_type, customer_currency)
        
    def calculate_shipping(self, destination_country, weight_kg):
        """Calculate international shipping"""
        return self.ecommerce.calculate_shipping_international(destination_country, weight_kg)
        
    # Banking Methods
    def send_bank_transfer(self, bank_code, account_number, amount, recipient_name, description=""):
        """Send bank transfer"""
        return self.bank_transfer.send_bank_transfer(bank_code, account_number, amount, recipient_name, description)
        
    def get_supported_banks(self):
        """Get supported banks"""
        return self.bank_transfer.get_supported_banks()
        
    def validate_bank_account(self, bank_code, account_number):
        """Validate bank account"""
        return self.bank_transfer.validate_bank_account(bank_code, account_number)
        
    # Real Exchange Rates
    def get_real_exchange_rate(self, currency):
        """Get real exchange rate from multiple sources"""
        return self.real_rates.get_multiple_sources_rate(currency)
        
    def get_all_real_rates(self, currencies):
        """Get real rates for multiple currencies"""
        return self.real_rates.get_all_real_rates(currencies)
        
    # BRICS Methods (delegated)
    def send_brics_payment(self, to_currency, amount_idr, recipient_address, fee_type='individual'):
        return self.brics_gateway.send_brics_payment(to_currency, amount_idr, recipient_address, fee_type)
        
    def receive_brics_payment(self, from_currency, amount_foreign, sender_address, fee_type='individual'):
        return self.brics_gateway.receive_brics_payment(from_currency, amount_foreign, sender_address, fee_type)
        
    def get_brics_currency_info(self, currency):
        return self.brics_gateway.get_brics_currency_info(currency)
        
    def get_brics_fee_quote(self, from_currency, to_currency, amount, fee_type='individual'):
        return self.brics_gateway.get_brics_fee_quote(from_currency, to_currency, amount, fee_type)

def demo_enhanced_system():
    """Demo enhanced system dengan vertical solutions"""
    print("🚀 iPayTools ENHANCED - VERTICAL SOLUTIONS DEMO")
    print("=" * 50)
    
    try:
        tools = iPayToolsEnhanced()
        print("✅ Enhanced system initialized")
        
        # Demo education vertical
        print("\n🎓 EDUCATION VERTICAL:")
        course_payment = tools.pay_course_fee("PYTHON101", "STU123", 500000, "USD")
        print(f"   💰 Course payment: {course_payment['transaction_id']}")
        
        # Demo e-commerce vertical  
        print("\n🛒 E-COMMERCE VERTICAL:")
        order_payment = tools.process_online_payment("ORD456", 250000, "SGD", "SG")
        print(f"   💰 Order payment: {order_payment['transaction_id']}")
        
        # Demo banking
        print("\n🏦 BANKING INTEGRATION:")
        banks = tools.get_supported_banks()
        print(f"   📊 Supported banks: {len(banks)} banks")
        
        # Demo real rates
        print("\n💰 REAL EXCHANGE RATES:")
        rates = tools.get_all_real_rates(['CNY', 'USD', 'SGD'])
        for currency, rate in rates.items():
            print(f"   💵 {currency}: {rate} IDR")
            
        print("\n🎉 ENHANCED SYSTEM READY FOR PRODUCTION!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")

if __name__ == "__main__":
    demo_enhanced_system()
