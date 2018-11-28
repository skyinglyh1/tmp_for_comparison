from boa.interop.System.ExecutionEngine import GetExecutingScriptHash
from boa.builtins import ToScriptHash, concat, state
from boa.interop.System.Runtime import CheckWitness, Notify, GetTime
from boa.interop.System.Storage import Get, GetContext, Put, Delete
from boa.interop.Ontology.Native import Invoke
from boa.interop.Ontology.Contract import Migrate

initial_name = "SnowBall Exchange"
initial_symbol = "SBE"
# SBE token decimal
decimal_ = 9
# dividend fee without referral = 19 (dividends to all token holders) + 1 （commission)
dividendFee0_ = 20
# dividend fee with only direct referral, 14 = 4 (directReferralFee_) + 10 (dividends to all token holders)
# dividend fee with both direct and indirect referral, 14 = 4 (directReferralFee_) + 1(indirectReferrlFee_) + 9(dividends to all token holders)
dividendFee1_ = 14
# direct referral bonus
directReferralFee_ = 4
# indirect referral bonus
indirectReferralFee_ = 1

managerExtraDividendPercentage_ = 25

# 0.0001 ONG
initialTokenPrice_ = 100000
# 0.00001 ONG
initialTokenPriceIncremental_ = 10000
# Ong decimal is 9
ongMagnitude_ = 1000000000
# tokenMagnitude_ = Pwr(10, decimal_)
tokenMagnitude_ = 1000000000

# multiply _dividends to make it dividable to _oldFakeTotalSupply, we will divide _profitPerToken when we actually use it
# largeNumber_ = Pwr(10, 30)
largeNumber_ = 1000000000000000000000000000000

# stake requirement (defaults at 200 tokens)
# referralStakeRequirement_ = Mul(200, tokenMagnitude_)
referralStakeRequirement_ = 200000000000

# ongContractAddress_ = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02')
ONGContractAddress_ = ToScriptHash("AFmseVrdL9f9oyCzZefL9tG6UbvhfRZMHJ")
selfContractAddr_ = GetExecutingScriptHash()

admin_ = ToScriptHash("AQf4Mzu1YJrhz9f3aRkkwSm9n3qhXGSh4p")

ADMIN_SUFFIX = bytearray(b'\x01')
MANAGER_SUFFIX = bytearray(b'\x02')
REFERREDBY_SUFFIX = bytearray(b'\0x03')
TOKEN_BALANCE_SUFFIX = bytearray(b'\x04')
ONG_BALANCE_SUFFIX = bytearray(b'\0x05')
DIVIDEND_VAULT_SUFFIX = bytearray(b'\x06')
REFERRAL_BALANCE_SUFFIX = bytearray(b'\x07')
PROFIT_PER_TOKEN_FROM_SUFFIX = bytearray(b'\0x8')
WITHDRAWN_EARNINGS_SUFFIX = bytearray(b'\0x9')

NAME_KEY = "name"
SYMBOL_KEY = "symbol"
DECIMALS_KEY = "decimal"
DEPLOYED_KEY = "deployed"
ANTI_EARLY_WHALE_KEY = "anti_early_whale"
TOTAL_SUPPLY_KEY = "total_supply"
FAKE_TOTAL_SUPPLY_FOR_HOLDER_DIVIDENDS_KEY = "total_supply_for_holder_dividends"
TOTAL_ONG_KEY = "total_ong"
TOTAL_ONG_FOR_TOKEN_KEY = "total_ong_for_key"
INITIAL_TOKEN_PRICE = "initial_price"
INITIAL_TOKEN_PRICE_INCREMENTAL = "initial_price_incremental"
PRICE_PER_TOKEN_KEY = "price_per_token"
PROFIT_PER_TOKEN_KEY = "profit_per_token"
REFERRAL_STAKE_REQUIREMENT_KEY = "referral_stake_require"
COMMISSION_KEY = "comission"

# for the convenience of usage, we will put 10^5 in the storage, decided by initialTokenPriceIncremental_ and  tokenMagnitude_
QUANTITY_INCREASE_PER_PRICE_KEY = "deltaQ_to_deltaP"

_POSITIVE_ = "Y"
_NEGATIVE_ = "N"

# 10000 ONG, when the total ONG balance is smaller than this, manager can buy 100 at maximum
# AntiEarlyWhaleQuota_ = Mul(10000, ongMagnitude_)
AntiEarlyWhaleQuota_ = 10000000000000

# adminQuota_ = Mul(1000, ongMagnitude_)
adminQuota_ = 1000000000000

# once a manager has bought 100 ong worth token, he cannot buy more before initial stage ends
# managerQuota_ = Mul(100, ongMagnitude_)
managerQuota_ = 100000000000

# once a normal customer has bought 25 ong worth token, he cannot buy more before initial stage ends
# customerQuota_ = Mul(10, ongMagnitude_)
customerQuota_ = 25000000000


def Main(operation, args):
    ############# Methods for Admin Starts ###############
    if operation == "init":
        return init()
    if operation == "addManager":
        if len(args) == 2:
            adminAddr = args[0]
            newManagerAddr = args[1]
            return addManager(adminAddr, newManagerAddr)
        else:
            Notify("addManager function should have 2 parameters")
            return False
    if operation == "setStakeRequirement":
        if len(args) == 2:
            admin = args[0]
            stakeRequirement = args[1]
            return setStakeRequirement(admin, stakeRequirement)
        else:
            Notify("setStakeRequirement function should have 2 parameters")
            return False
    if operation == "setName":
        if len(args) == 2:
            admin = args[0]
            name = args[1]
            return setName(admin, name)
        else:
            Notify("setName function should have 2 parameters")
            return False
    if operation == "setSymbol":
        if len(args) == 2:
            admin = args[0]
            symbol = args[1]
            return setSymbol(admin, symbol)
        else:
            Notify("setSymbol function should have 2 parameters")
            return False
    if operation == "cancelAntiEarlyWhale":
        if len(args) == 1:
            account = args[0]
            return cancelAntiEarlyWhale(account)
        else:
            return False
    if operation == "transferOwnership":
        if len(args) == 2:
            fromAcct = args[0]
            toAcct = args[1]
            return transferOwnership(fromAcct, toAcct)
        else:
            return False
    if operation == "dropONGForHolders":
        if len(args) == 2:
            account = args[0]
            ongAmount = args[1]
            return dropONGForHolders(account, ongAmount)
        else:
            return False
    if operation == "withdrawCommission":
        if len(args) == 1:
            account = args[0]
            return withdrawCommission(account)
        else:
            return False
    if operation == "migrateContract":
        if len(args) == 9:
            account = args[0]
            code = args[1]
            needStorage = args[2]
            name = args[3]
            version = args[4]
            author = args[5]
            email = args[6]
            description = args[7]
            newContractHash = args[8]
            return migrateContract(account, code, needStorage, name, version, author, email, description, newContractHash)
        else:
            return False
    ################  Methods for Admin Ends  ###############
    ################ Methods for Users Starts ###############
    if operation == "buy":
        if len(args) == 3:
            account = args[0]
            ongAmount = args[1]
            directReferral = args[2]
            return buy(account, ongAmount, directReferral)
        else:
            Notify("buy function should have 3 parameters")
            return False
    if operation == "reinvest":
        if len(args) == 1:
            account = args[0]
            return reinvest(account)
        else:
            Notify("reinvest function should only have 1 parameter")
            return False
    if operation == "sell":
        if len(args) == 2:
            account = args[0]
            tokenAmount = args[1]
            return sell(account, tokenAmount)
        else:
            Notify("sell function should 2 parameters")
            return False
    if operation == "withdraw":
        if len(args) == 1:
            account = args[0]
            return withdraw(account)
        else:
            Notify("withdraw function should only have 1 parameter")
            return False
    if operation == "exitOut":
        if len(args) == 1:
            account = args[0]
            return exitOut(account)
        else:
            Notify("exitOut function should have 1 parameter")
            return False
    ################ Methods for Users Ends ###############
    ############# Methods for Global info Starts ###############
    if operation == "totalSupply":
        return totalSupply()
    if operation == "fakeTotalSupply":
        return fakeTotalSupply()
    if operation == "totalOngAmount":
        return totalOngAmount()
    if operation == "totalOngAmountForKey":
        return totalOngAmountForKey()
    if operation == "getName":
        return getName()
    if operation == "getSymbol":
        return getSymbol()
    if operation == "getDecimals":
        return getDecimals()
    if operation == "getStakeRequirement":
        return getStakeRequirement()
    if operation == "getPrice":
        return getPrice()
    if operation == "getCommissionAmount":
        return getCommissionAmount()
    ############# Methods for Global info Ends ###############
    ############### Methods for Users' info Starts ###############
    if operation == "getBalanceOf":
        if len(args) == 1:
            addr = args[0]
            return getBalanceOf(addr)
        else:
            Notify("balanceOf function should have 1 parameter")
            return False
    if operation == "getDividendBalanceOf":
        if len(args) == 1:
            addr = args[0]
            return getDividendBalanceOf(addr)
        else:
            Notify(["dividendOf---", len(args)])
            return False
    if operation == "getReferralBalanceOf":
        if len(args) == 1:
            addr = args[0]
            return getReferralBalanceOf(addr)
        else:
            Notify("referralBalanceOf function should have 1 parameter")
            return False
    if operation == "getOngBalanceOf":
        if len(args) == 1:
            addr = args[0]
            return getOngBalanceOf(addr)
        else:
            Notify("ongBalanceOf function should have 1 parameter")
            return False
    if operation == "getDividendsBalancesOf":
        if len(args) == 1:
            addr = args[0]
            return getDividendsBalancesOf(addr)
        else:
            return False
    if operation == "getDividendsBalanceOf":
        if len(args) == 1:
            addr = args[0]
            return getDividendsBalanceOf(addr)
        else:
            return False
    if operation == "getWithdrawnEarnings":
        if len(args) == 1:
            addr = args[0]
            return getWithdrawnEarnings(addr)
        else:
            return False

    if operation == "directReferralOf":
        if len(args) == 1:
            addr = args[0]
            return directReferralOf(addr)
        else:
            Notify("directReferralOf function should have 1 parameter")
            return False
    ############### Methods for Users' info Ends ###############
    ############## Methods for Utility purpose Starts ##########
    if operation == "checkAdmin":
        if len(args) == 1:
            addr = args[0]
            return checkAdmin(addr)
        else:
            Notify("checkAdmin function should have 1 parameter")
            return False
    if operation == "checkManager":
        if len(args) == 1:
            addr = args[0]
            return checkManager(addr)
        else:
            Notify("checkManager function should have 1 parameter")
            return False
    if operation == "_collectDividendOf":
        if len(args) == 1:
            addr = args[0]
            return _collectDividendOf(addr)
        else:
            Notify("_collectDividendOf function should have 1 parameter")
            return False
    if operation == "_calculateBuyOngToToken":
        if len(args) == 1:
            _ongAmount = args[0]
            return _calculateBuyOngToToken(_ongAmount)
        else:
            Notify("_ongToToken function should have 1 parameter")
            return False
    if operation == "_calculateSellTokenToOng":
        if len(args) == 1:
            _tokenAmount = args[0]
            return _calculateSellTokenToOng(_tokenAmount)
        else:
            Notify("_tokenToOng function should have 1 parameter")
            return False
        ############## Methods for Utility purpose Starts ##########

    return False



#======================= Methods for Admin Starts =============
def init():
    """
    can only be run once
    :return:
    """
    deployed = Get(GetContext(), DEPLOYED_KEY)

    if deployed != _POSITIVE_:

        # only admin can deploy the contract
        RequireWitness(admin_)

        # Set admin
        admin_key = _concatKey(admin_, ADMIN_SUFFIX)
        Put(GetContext(), admin_key, _POSITIVE_)

        # Set Avalanche managers (set as both admin and manager)
        manager1 = ToScriptHash("AQf4Mzu1YJrhz9f3aRkkwSm9n3qhXGSh4p")
        key = _concatKey(manager1, MANAGER_SUFFIX)
        Put(GetContext(), key, _POSITIVE_)

        manager2 = ToScriptHash("AcY5o2xpK5tZdPjKDhrVE82VMtHeK1hoAx")
        key = _concatKey(manager2, MANAGER_SUFFIX)
        Put(GetContext(), key, _POSITIVE_)
        #  can add manager2, 3, 4, 5, 6

        # set name info
        Put(GetContext(), NAME_KEY, initial_name)
        # set symbol info
        Put(GetContext(), SYMBOL_KEY, initial_symbol)
        # set decimal info, decimal_ cannot be changed
        Put(GetContext(), DECIMALS_KEY, decimal_)

        # set anti early whale key as true for the early stage
        Put(GetContext(), ANTI_EARLY_WHALE_KEY, _POSITIVE_)
        # initiate totalSupply
        Put(GetContext(), TOTAL_SUPPLY_KEY, 0)
        # initiate fakeTotalSupply
        Put(GetContext(), FAKE_TOTAL_SUPPLY_FOR_HOLDER_DIVIDENDS_KEY, 0)
        # initiate total ONG Balance
        Put(GetContext(), TOTAL_ONG_KEY, 0)

        # initiate initialTokenPrice_ and initialTokenPriceIncremental_
        Put(GetContext(), INITIAL_TOKEN_PRICE, initialTokenPrice_)
        Put(GetContext(), INITIAL_TOKEN_PRICE_INCREMENTAL, initialTokenPriceIncremental_)
        # initiate pricePerToken
        Put(GetContext(), PRICE_PER_TOKEN_KEY, initialTokenPrice_)
        # initiate profit per token
        Put(GetContext(), PROFIT_PER_TOKEN_KEY, 0)
        # initial team_ info
        Put(GetContext(), COMMISSION_KEY, 0)
        # initiate referral requirement
        Put(GetContext(), REFERRAL_STAKE_REQUIREMENT_KEY, referralStakeRequirement_)

        # save the ratio for the convenience of usage
        Put(GetContext(), QUANTITY_INCREASE_PER_PRICE_KEY, Div(tokenMagnitude_, initialTokenPriceIncremental_))

        # Mark the contract has been deployed
        Put(GetContext(), DEPLOYED_KEY, _POSITIVE_)

        Notify(["congrats, admin, you have deployed the contract successfuly!"])
    else:
        Notify(["Idiot admin, the contract has already been deployed!"])
        return False
    return True

def addManager(adminAddr, newManagerAddr):
    """
    Add manager, only admin can add new manager
    :param addr: the address that will be added as a new manager
    :return:
    """
    # check if the address is legal
    RequireScriptHash(adminAddr)
    RequireScriptHash(newManagerAddr)
    RequireWitness(adminAddr)
    # check if adminAddr is admin
    Require(checkAdmin(adminAddr))
    Put(GetContext(), _concatKey(newManagerAddr, MANAGER_SUFFIX), _POSITIVE_)
    return True

def setStakeRequirement(adminAddr, stakeRequirement):
    RequireWitness(adminAddr)
    Require(checkAdmin(adminAddr))
    Put(GetContext(), REFERRAL_STAKE_REQUIREMENT_KEY, stakeRequirement)
    return True

def setName(adminAddr, name):
    RequireWitness(adminAddr)
    Require(checkAdmin(adminAddr))
    Put(GetContext(), NAME_KEY, name)
    return True

def setSymbol(adminAddr, symbol):
    RequireWitness(adminAddr)
    Require(checkAdmin(adminAddr))
    Put(GetContext(), SYMBOL_KEY, symbol)
    return True

def cancelAntiEarlyWhale(adminAddr):
    """
    In case the project doesn't draw much attention, only admin can cannel anti early whale in order to open the
    buy opportunity to everyone
    :param adminAddr:
    :return:
    """
    RequireWitness(adminAddr)
    Require(checkAdmin(adminAddr))
    Put(GetContext(), ANTI_EARLY_WHALE_KEY, _NEGATIVE_)
    return True

def transferOwnership(fromAcct, toAcct):
    RequireScriptHash(fromAcct)
    RequireScriptHash(toAcct)
    RequireWitness(fromAcct)
    Require(checkAdmin(fromAcct))
    Delete(GetContext(), _concatKey(fromAcct, ADMIN_SUFFIX))
    Put(GetContext(), _concatKey(toAcct, ADMIN_SUFFIX), _POSITIVE_)
    return True

def dropONGForHolders(account, ongAmount):
    Require(_transferONG(account, selfContractAddr_, ongAmount))
    # update total ong amount
    Put(GetContext(), TOTAL_ONG_KEY, Add(totalOngAmount(), ongAmount))

    # update profit per token
    _profitPerToken = Get(GetContext(), PROFIT_PER_TOKEN_KEY)
    _fakeTotalSupply = fakeTotalSupply()
    if _fakeTotalSupply != 0:
        _profitPerTokenToBeAdd = Div(Mul(ongAmount, largeNumber_), _fakeTotalSupply)
    else:
        Put(GetContext(), COMMISSION_KEY, Add(getCommissionAmount(), ongAmount))
    return True

def withdrawCommission(account):
    Require(checkAdmin(account))
    RequireWitness(account)
    Require(_transferONGFromContact(admin_, getCommissionAmount()))

    Put(GetContext(), TOTAL_ONG_KEY, Sub(totalOngAmount(), getCommissionAmount()))
    Delete(GetContext(), COMMISSION_KEY)
    return True

def migrateContract(account, code, needStorage, name, version, author, email, description, newContractHash):
    Require(checkAdmin(account))
    res = _transferONGFromContact(newContractHash, totalOngAmount())
    Require(res)
    if res == True:
        res = Migrate(code, needStorage, name, version, author, email, description)
        Require(res)
        Notify(["Migrate Contract successfully", account, GetTime()])
        return True
    else:
        Notify(["MigrateContractError", "transfer ONG to new contract error"])
        return False
#======================= Methods for Admin Ends =============





# ==================== Methods for Users Starts ========================
def buy(account, ongAmount, directReferral):
    """
    Converts all incoming ong to tokens for the caller,
    pass and save the directReferral and indirectReferral address (if any)
    :param account:
    :param ongAmount:
    :param directReferral: if yes, pass in; if no, pass
    :return: _purchaseTokenAmount
    """
    # make sure account is legal
    RequireScriptHash(account)
    RequireWitness(account)
    # account buy tokens for the first time
    if getBalanceOf(account) == 0 and directReferral != account and directReferralOf(account) == False:
        # directReferral is legal
        if len(directReferral) == 20 and checkReferralRequirement(directReferral):
            # record account is referred by directReferral
            Put(GetContext(), _concatKey(account, REFERREDBY_SUFFIX), directReferral)

    # collect the presentdividend to the dividend vault of _account before he buys more tokens
    _collectDividendOf(account)

    return _purchaseToken(account, ongAmount)


def reinvest(_account):
    """
    Converts all the caller's dividend and referral earnings to tokens
    """
    RequireWitness(_account)
    # put present dividend into dividend vault, update profit per token and dividend vault
    _collectDividendOf(_account)
    # add dividend vault and referral balance together to get _dividends
    _dividends = getDividendsBalanceOf(_account)
    _ongBalance = getOngBalanceOf(_account)
    _ongAmount = Add(_dividends, _ongBalance)

    Require(_antiEarlyWhale(_account, _ongAmount))

    # delete referral balance, dividend balance and ong balance of account
    Delete(GetContext(), _concatKey(_account, REFERRAL_BALANCE_SUFFIX))
    Delete(GetContext(), _concatKey(_account, DIVIDEND_VAULT_SUFFIX))
    Delete(GetContext(), _concatKey(ONG_BALANCE_SUFFIX, _account))


    # _dividends that is used to distribute to all the token holders
    _dividends = 0
    # referral of the _account
    _directReferral = directReferralOf(_account)
    _oldTotalTokenSupply = totalSupply()
    if _oldTotalTokenSupply != 0:
        if _directReferral != False:
            # Has referral, the dividend fee will be 14%,
            _dividends = Div(Mul(_ongAmount, dividendFee1_), 100)
        else:
            # No referral, the dividend fee will be 20%,
            _dividends = Div(Mul(_ongAmount, dividendFee0_), 100)
    # if one person buys token at the first beginning, he can buy tokens with all his ong, which means no _dividends
    else:
        # make sure only admin can buy as the first participant of this project
        Require(checkAdmin(_account))
    # _pureOngAmount will be used to purchase token
    _pureOngAmount = Sub(_ongAmount, _dividends)
    _purchaseTokenAmount = _calculateBuyOngToToken(_pureOngAmount)

    _newTotalTokenSupply = Add(_oldTotalTokenSupply, _purchaseTokenAmount)
    #  the new total Supply should be greater than the old one to avoid outflow
    Require(_newTotalTokenSupply > _oldTotalTokenSupply)

    # note that manager can earn 25% more in terms of holder share, but his token balance doesn't change
    _oldFakeTotalSupply = fakeTotalSupply()
    _newFakeTotalSupply = 0
    if checkManager(_account):
        _newFakeTotalSupply = Add(_oldFakeTotalSupply, Div(Mul(_purchaseTokenAmount, Add(100, managerExtraDividendPercentage_)), 100))
    else:
        _newFakeTotalSupply = Add(_oldFakeTotalSupply, _purchaseTokenAmount)
    Require(_newFakeTotalSupply > _oldFakeTotalSupply)

    # Now let's make actual changes in the ledger
    if _directReferral != False:
        # calculate the direct referral bonus, 4% of _ongAmount
        _directReferralBonus = Div(Mul(_ongAmount, directReferralFee_), 100)
        #  add the direct referral bonus to the referral balance
        _newDirectReferralBalance = Add(getReferralBalanceOf(_directReferral), _directReferralBonus)
        Put(GetContext(), _concatKey(_directReferral, REFERRAL_BALANCE_SUFFIX), _newDirectReferralBalance)
        # Update the _dividends
        _dividends = Sub(_dividends, _directReferralBonus)
        # get the indirect referral <=> the referral of the referral of the _account
        _indirectReferral = directReferralOf(_directReferral)
        # if _account also has indirect referral,
        if _indirectReferral != False:
            # calculate the indirect refreral bonus, 1% of _ongAmount
            _indirectReferralBonus = Div(Mul(_ongAmount, indirectReferralFee_), 100)
            # add the indirect referral bonus to the indirect referral balance
            _newIndirectReferralBalance = Add(getReferralBalanceOf(_indirectReferral), _indirectReferralBonus)
            Put(GetContext(), _concatKey(_indirectReferral, REFERRAL_BALANCE_SUFFIX), _newIndirectReferralBalance)
            # Update the _dividends, 9% of _ongAmount
            _dividends = Sub(_dividends, _indirectReferralBonus)
        # if _account has no indirect referral, 10% of _ongAmount will be the final _dividends
    #  add condition to avoid the first person who buys tokens to give 1% to team
    elif _oldFakeTotalSupply != 0:
        # This 1% will be treated as commission
        _commission_part = Div(_ongAmount, 100)
        _newCommissionAmount = Add(getCommissionAmount(), _commission_part)
        Put(GetContext(), COMMISSION_KEY, _newCommissionAmount)
        # Update the _dividends, the left 19% of _ongAmount will go to token holders
        _dividends = Sub(_dividends, _commission_part)

    # _dividends will be distributed to all the token holders, indicated through profitPerToken
    _profitPerToken = Get(GetContext(), PROFIT_PER_TOKEN_KEY)
    # if the buyer is not the first person to buy tokens
    if _oldFakeTotalSupply != 0:
        # multiply _dividends to make it dividable to _oldFakeTotalSupply, we will divide _profitPerToken when we actually use it
        _dividends = Mul(_dividends, largeNumber_)
        # the _account do not have the right to share the _dividends
        _profitPerToken = Add(Div(_dividends, _oldFakeTotalSupply), _profitPerToken)
        # Update the _profitPerToken
        Put(GetContext(), PROFIT_PER_TOKEN_KEY, _profitPerToken)
    else:
        if _dividends > 0:
            Put(GetContext(), COMMISSION_KEY, Add(getCommissionAmount(), _dividends))

    # record the _profitPerToken value after the _account buys in for _account to count his share till _profitPerToken later
    Put(GetContext(), _concatKey(_account, PROFIT_PER_TOKEN_FROM_SUFFIX), _profitPerToken)

    # Update the token balance of _account
    Put(GetContext(), _concatKey(_account, TOKEN_BALANCE_SUFFIX), Add(getBalanceOf(_account), _purchaseTokenAmount))
    # Update the totalSupply of token
    Put(GetContext(), TOTAL_SUPPLY_KEY, _newTotalTokenSupply)
    # Update the fakeTotalSupply of token
    Put(GetContext(), FAKE_TOTAL_SUPPLY_FOR_HOLDER_DIVIDENDS_KEY, _newFakeTotalSupply)

    # Update total ONG balance of this contract
    _newtotalOngAmount = Add(totalOngAmount(), _ongAmount)
    Put(GetContext(), TOTAL_ONG_KEY, _newtotalOngAmount)

    # Update ONG balance of this contract for key
    _newtotalOngAmountForKey = Add(totalOngAmountForKey(), _pureOngAmount)
    Put(GetContext(), TOTAL_ONG_FOR_TOKEN_KEY, _newtotalOngAmountForKey)


    _onReinvest(_account, _dividends, _ongAmount)
    return True

def sell(_account, _tokenAmount):
    """
    sell the _tokenAmount tokens
    :param _account:
    :param _tokenAmount:
    :return: the ong amount for selling _tokenAmount of tokens
    """

    RequireWitness(_account)
    # Make sure _account's balance is greater than _tokenAmount that is gonna be sold
    _tokenBalance = getBalanceOf(_account)
    Require(_tokenAmount <= _tokenBalance)
    _ongAmount = _calculateSellTokenToOng(_tokenAmount)

    # referral of the _account
    _directReferral = directReferralOf(_account)

    # _dividends that is used to distribute to all the token holders
    _dividends = 0
    if _directReferral != False:
        # Has referral, the dividend fee will be 14%,
        _dividends = Div(Mul(_ongAmount, dividendFee1_), 100)
    else:
        # No referral, the dividend fee will be 20%,
        _dividends = Div(Mul(_ongAmount, dividendFee0_), 100)
    # _pureOngAmount will be used the income when you sell _tokenAmount of tokens
    _pureOngAmount = Sub(_ongAmount, _dividends)
    _oldTotalTokenSupply = totalSupply()
    _newTotalTokenSupply = Sub(_oldTotalTokenSupply, _tokenAmount)
    #  the new total Supply should be less than the old one to avoid underflow
    Require(_newTotalTokenSupply < _oldTotalTokenSupply)

    # note that manager can earn 50% more in terms of holder share, but his token balance doesn't change
    _oldFakeTotalSupply = fakeTotalSupply()
    _newFakeTotalSupply = 0
    if checkManager(_account):
        _newFakeTotalSupply = Sub(_oldFakeTotalSupply, Div(Mul(_tokenAmount, Add(100, managerExtraDividendPercentage_)), 100))
    else:
        _newFakeTotalSupply = Sub(_oldFakeTotalSupply, _tokenAmount)
    Require(_newFakeTotalSupply < _oldFakeTotalSupply)


    # Now let's make actual changes in the ledger
    if  _directReferral != False:
        # calculate the direct referral bonus, 4% of _ongAmount
        _directReferralBonus = Div(Mul(_ongAmount, directReferralFee_), 100)
        #  add the direct referral bonus to the referral balance
        _newDirectReferralBalance = Add(getReferralBalanceOf(_directReferral), _directReferralBonus)
        Put(GetContext(), _concatKey(_directReferral, REFERRAL_BALANCE_SUFFIX), _newDirectReferralBalance)
        # Update the _dividends from _account
        _dividends = Sub(_dividends, _directReferralBonus)
        # get the indirect referral <=> the referral of the referral of the _account
        _indirectReferral = directReferralOf(_directReferral)

        # if _account also has indirect referral,
        if _directReferral != False:
            # calculate the indirect refreral bonus, 1% of _ongAmount
            _indirectReferralBonus = Div(Mul(_ongAmount, indirectReferralFee_), 100)
            # add the indirect referral bonus to the indirect referral balance
            _newIndirectReferralBalance = Add(getReferralBalanceOf(_indirectReferral), _indirectReferralBonus)
            Put(GetContext(), _concatKey(_indirectReferral, REFERRAL_BALANCE_SUFFIX), _newIndirectReferralBalance)
            # Update the _dividends from _account, 9% of _ongAmount
            _dividends = Sub(_dividends, _indirectReferralBonus)
        # if _account has no indirect referral, 10% of _ongAmount will be the final _dividends
    else:
        # This 1% will be treated as commission
        _commission_part = Div(_ongAmount, 100)
        _newCommissionAmount = Add(getCommissionAmount(), _commission_part)
        Put(GetContext(), COMMISSION_KEY, _newCommissionAmount)
        # Update the _dividends, the left 19% of _ongAmount will go to token holders
        _dividends = Sub(_dividends, _commission_part)

    # put present dividend into dividend vault, update profit per token and dividend vault, should collect before we update _profitPerToken
    _collectDividendOf(_account)

    # calculate how many token left for _account
    _tokenLeft = Sub(_tokenBalance, _tokenAmount)

    # _dividends will be distributed to all the token holders, indicated through profitPerToken
    _profitPerToken = Get(GetContext(), PROFIT_PER_TOKEN_KEY)

    _newProfitPerToken = 0
    # if there still exist tokens after _account sells out his tokens
    if _newTotalTokenSupply != 0:
        # multiply _dividends to make it dividable to _oldFakeTotalSupply, we will divide _profitPerToken when we actually use it
        _dividends = Mul(_dividends, largeNumber_)
        # the _account do not have the right to share the _dividends
        _newProfitPerToken = Add(Div(_dividends, _newFakeTotalSupply), _profitPerToken)
        # Update the _profitPerToken
        Put(GetContext(), PROFIT_PER_TOKEN_KEY, _newProfitPerToken)
        # update token balance of _account
        if _tokenLeft > 0:
            # Update the token balance of _account
            Put(GetContext(), _concatKey(_account, TOKEN_BALANCE_SUFFIX), _tokenLeft)
        else:
            # if _account sells out all his tokens, make sure profit per token after he sells is 0
            Delete(GetContext(), _concatKey(_account, PROFIT_PER_TOKEN_FROM_SUFFIX))
            Delete(GetContext(), _concatKey(_account, TOKEN_BALANCE_SUFFIX))
    else:
        # if the total supply is 0 after _account sells out his tokens, all the sharing dividends will go to team_ referral balance since there are token holders
        if _dividends > 0:
            Put(GetContext(), COMMISSION_KEY, Add(getCommissionAmount(), _dividends))

    # Update the ong balance of _account
    _ongBalanceOfAccount = Add(getOngBalanceOf(_account), _pureOngAmount)
    Put(GetContext(), _concatKey(_account, ONG_BALANCE_SUFFIX), _ongBalanceOfAccount)

    # Update the totalSupply of token
    Put(GetContext(), TOTAL_SUPPLY_KEY, _newTotalTokenSupply)

    # Update the fakeTotalSupply of token
    Put(GetContext(), FAKE_TOTAL_SUPPLY_FOR_HOLDER_DIVIDENDS_KEY, _newFakeTotalSupply)

    # Update ONG balance of this contract for key
    _newtotalOngAmountForKey = Sub(totalOngAmountForKey(), _pureOngAmount)
    Put(GetContext(), TOTAL_ONG_FOR_TOKEN_KEY, _newtotalOngAmountForKey)

    # Broadcast the event
    _onTokenSell(_account, _tokenAmount, _pureOngAmount)

    return True




def withdraw(_account):
    """
    Withdraw all the caller earning including dividends and referral bonus and the ong balance from selling the keys
    :param _account:
    :return: the withdrawn ong amount
    """
    RequireWitness(_account)
    # put present dividend into dividend vault, update profit per token and dividend vault
    _collectDividendOf(_account)
    # add dividend vault and referral balance together to get _dividends
    _dividends = getDividendsBalanceOf(_account)
    # _account balance from selling keys
    _ongBalance = getOngBalanceOf(_account)
    # add two together as earnings
    _ongAmount = Add(_dividends, _ongBalance)
    # make sure _account has some earnings
    Require(_ongAmount > 0)

    # transfer _dividends ( his ONG ) to _account
    Require(_transferONGFromContact(_account, _ongAmount))

    # Update dividend
    Delete(GetContext(), _concatKey(_account, DIVIDEND_VAULT_SUFFIX))
    # Update referral bonus
    Delete(GetContext(), _concatKey(_account, REFERRAL_BALANCE_SUFFIX))
    # Update ong balance of _account
    Delete(GetContext(), _concatKey(_account, ONG_BALANCE_SUFFIX))

    # Update withdrawn earnings ledger
    _newWithdrawnEarnings = Add(getWithdrawnEarnings(_account), _ongAmount)
    Put(GetContext(), _concatKey(_account, WITHDRAWN_EARNINGS_SUFFIX), _newWithdrawnEarnings)

    # Update ONG balance of this contract (need to be updated only when withdraw() is invoked)
    _totalOngAmount = Sub(totalOngAmount(), _ongAmount)
    Put(GetContext(), TOTAL_ONG_KEY, _totalOngAmount)

    _onWithdraw(_account, _ongAmount)

    return True

def exitOut(_account):
    """
    sell all the tokens and collect the dividend and referral bonus, then withdraw all the money
    :param _account:
    :return: all the ong amount to be withdrawn when exit
    """
    RequireWitness(_account)
    _tokenBalance = getBalanceOf(_account)
    if _tokenBalance > 0:
        sell(_account, _tokenBalance)

    withdraw(_account)
    return True

#======================= Methods for Users Ends=============



# ======================== Methods for Global info Starts =============================
def totalSupply():
    return Get(GetContext(), TOTAL_SUPPLY_KEY)

def fakeTotalSupply():
    return Get(GetContext(), FAKE_TOTAL_SUPPLY_FOR_HOLDER_DIVIDENDS_KEY)

def totalOngAmount():
    return Get(GetContext(), TOTAL_ONG_KEY)

def totalOngAmountForKey():
    return Get(GetContext(), TOTAL_ONG_FOR_TOKEN_KEY)

def getName():
    return Get(GetContext(), NAME_KEY)

def getSymbol():
    return Get(GetContext(), SYMBOL_KEY)

def getDecimals():
    return Get(GetContext(), DECIMALS_KEY)

def getStakeRequirement():
    return Get(GetContext(), REFERRAL_STAKE_REQUIREMENT_KEY)

def getPrice():
    _totalSupply = totalSupply()
    _pricePerToken = Add(Div(Mul(_totalSupply, initialTokenPriceIncremental()), tokenMagnitude_), initialTokenPrice())
    return _pricePerToken

def getCommissionAmount():
    return Get(GetContext(), COMMISSION_KEY)
# ==================== Methods for Global info Ends =======================


# ==================== Methods for Users' info Starts =======================
def getBalanceOf(account):
    RequireScriptHash(account)
    return Get(GetContext(), _concatKey(account, TOKEN_BALANCE_SUFFIX))


def getDividendBalanceOf(account):
    RequireScriptHash(account)
    _unsharedProfitPerTokenFrom = profitPerTokenFromOf(account)
    _profitPerTokenNow = Get(GetContext(), PROFIT_PER_TOKEN_KEY)
    # if account is a manager, he will share 50% more of holder dividends
    _unsharedProfitIntervalPerToken = Sub(_profitPerTokenNow, _unsharedProfitPerTokenFrom)
    _sharedProfitTillNow = 0
    if _unsharedProfitIntervalPerToken != 0:
        _sharedRawProfitTillNow = 0
        if checkManager(account):
            _sharedRawProfitTillNow = Div(Mul(getBalanceOf(account), Mul(Add(100, managerExtraDividendPercentage_), _unsharedProfitIntervalPerToken )), 100)
        else:
            _sharedRawProfitTillNow = Mul(getBalanceOf(account), _unsharedProfitIntervalPerToken)
        # collect the present dividend to dividend vault
        _sharedProfitTillNow = Div(_sharedRawProfitTillNow, largeNumber_)
    dividendTillNow = Add(Get(GetContext(), _concatKey(account, DIVIDEND_VAULT_SUFFIX)), _sharedProfitTillNow)
    return dividendTillNow

def getReferralBalanceOf(account):
    """
    referral bonus of account
    :param account: the referal address
    :return: referral bonus earned by account
    """
    RequireScriptHash(account)
    return Get(GetContext(), _concatKey(account, REFERRAL_BALANCE_SUFFIX))


def getOngBalanceOf(account):
    RequireScriptHash(account)
    return Get(GetContext(), _concatKey(account, ONG_BALANCE_SUFFIX))

def getDividendsBalancesOf(account):
    """
    :param account:
    :return: [dividendBalance, referralBalance, ongBalance]
    """
    RequireScriptHash(account)
    return [getDividendBalanceOf(account), getReferralBalanceOf(account), getOngBalanceOf(account)]

def getDividendsBalanceOf(account):
    """
    dividends = dividend + referral bonus (if exist)
    :param account:
    :return:
    """
    RequireScriptHash(account)
    _dividend = getDividendBalanceOf(account)
    _referralBonus = getReferralBalanceOf(account)
    return Add(_dividend, _referralBonus)

def getWithdrawnEarnings(account):
    """
    To record how much has been withdrawn to account
    :param account:
    :return: ong amount of being withdrawn earnings to account
    """
    RequireScriptHash(account)
    return Get(GetContext(), _concatKey(account, WITHDRAWN_EARNINGS_SUFFIX))

def directReferralOf(account):
    """
    Get the direct referral of account
    :param account: the referrer
    :return: referraal address if exists, False if it does not exist
    """
    _directReferral = Get(GetContext(), _concatKey(account, REFERREDBY_SUFFIX))
    if len(_directReferral) == 20:
        return _directReferral
    else:
        return False
# ==================== Methods for Users' info Ends  =======================

# ==================== Methods for Utility purpose Starts =======================
def checkAdmin(account):
    """
    To make sure that
    1. the msg.sender is account
    2. account + ADMIN_PREFIX  <-> True : means account is the admin
    :param account:
    :return:
    """
    # check if the account is legal address
    RequireScriptHash(account)
    # Make sure the invocation comes from account
    # Require(CheckWitness(addr) == b'\x01') { code can run passing by Require(True)}
    value = Get(GetContext(), _concatKey(account, ADMIN_SUFFIX))
    if value == _POSITIVE_:
        return True
    else:
        return False

def checkManager(account):
    """
    To make sure that
    1. the msg.sender is account
    2. account + MANAGER_SUFFIX  <-> True : means account is one of the managers
    :param account:
    :return: True or False
    """
    # check if the account is legal
    RequireScriptHash(account)
    value = Get(GetContext(), _concatKey(account, MANAGER_SUFFIX))
    if value == _POSITIVE_:
        return True
    else:
        return False

def checkReferralRequirement(account):
    """
    when account has more tokens than referralStakeRequirement_, he can have his referral link or code to refer this project to others
    :param account:
    :return: True or False
    """
    RequireScriptHash(account)
    _referralStakeRequirement = Get(GetContext(), REFERRAL_STAKE_REQUIREMENT_KEY)
    if getBalanceOf(account) >= referralStakeRequirement_:
        return True
    else:
        return False

def initialTokenPrice():
    return Get(GetContext(), INITIAL_TOKEN_PRICE)

def initialTokenPriceIncremental():
    return Get(GetContext(), INITIAL_TOKEN_PRICE_INCREMENTAL)

def profitPerTokenFromOf(account):
    # before this value, addr cannot share profit, after this value, addr can share the holder dividends
    RequireScriptHash(account)
    return Get(GetContext(), _concatKey(account, PROFIT_PER_TOKEN_FROM_SUFFIX))



def _purchaseToken(_account, _ongAmount):
    """

    :param _account:
    :param _ongAmount:
    :return:
    """
    # avoid early whale
    RequireWitness(_account)

    Require(_antiEarlyWhale(_account, _ongAmount))
    # transfer ONG to contract, make sure it is successful
    Require(_transferONG(_account, selfContractAddr_, _ongAmount))

    # _dividends that is used to distribute to all the token holders
    _dividends = 0
    # referral of the _account
    _directReferral = directReferralOf(_account)
    _oldTotalTokenSupply = totalSupply()
    if _oldTotalTokenSupply != 0:
        if _directReferral != False:
            # Has referral, the dividend fee will be 14%,
            _dividends = Div(Mul(_ongAmount, dividendFee1_), 100)
        else:
            # No referral, the dividend fee will be 20%,
            _dividends = Div(Mul(_ongAmount, dividendFee0_), 100)
    # if one person buys token at the first beginning, he can buy tokens with all his ong, which means no _dividends
    else:
        # make sure only admin can buy as the first participant of this project
        Require(checkAdmin(_account))
    # _pureOngAmount will be used to purchase token
    _pureOngAmount = Sub(_ongAmount, _dividends)
    _purchaseTokenAmount = _calculateBuyOngToToken(_pureOngAmount)

    _newTotalTokenSupply = Add(_oldTotalTokenSupply, _purchaseTokenAmount)
    #  the new total Supply should be greater than the old one to avoid outflow
    Require(_newTotalTokenSupply > _oldTotalTokenSupply)

    # note that manager can earn 25% more in terms of holder share, but his token balance doesn't change
    _oldFakeTotalSupply = fakeTotalSupply()
    _newFakeTotalSupply = 0
    if checkManager(_account):
        _newFakeTotalSupply = Add(_oldFakeTotalSupply, Div(Mul(_purchaseTokenAmount, Add(100, managerExtraDividendPercentage_)), 100))
    else:
        _newFakeTotalSupply = Add(_oldFakeTotalSupply, _purchaseTokenAmount)
    Require(_newFakeTotalSupply > _oldFakeTotalSupply)
    # Now let's make actual changes in the ledger
    if _directReferral != False:
        # calculate the direct referral bonus, 4% of _ongAmount
        _directReferralBonus = Div(Mul(_ongAmount, directReferralFee_), 100)
        #  add the direct referral bonus to the referral balance
        _newDirectReferralBalance = Add(getReferralBalanceOf(_directReferral), _directReferralBonus)
        Put(GetContext(), _concatKey(_directReferral, REFERRAL_BALANCE_SUFFIX), _newDirectReferralBalance)
        # Update the _dividends
        _dividends = Sub(_dividends, _directReferralBonus)
        # get the indirect referral <=> the referral of the referral of the _account
        _indirectReferral = directReferralOf(_directReferral)
        # if _account also has indirect referral,
        if _indirectReferral != False:
            # calculate the indirect refreral bonus, 1% of _ongAmount
            _indirectReferralBonus = Div(Mul(_ongAmount, indirectReferralFee_), 100)
            # add the indirect referral bonus to the indirect referral balance
            _newIndirectReferralBalance = Add(getReferralBalanceOf(_indirectReferral), _indirectReferralBonus)
            Put(GetContext(), _concatKey(_indirectReferral, REFERRAL_BALANCE_SUFFIX), _newIndirectReferralBalance)
            # Update the _dividends, 9% of _ongAmount
            _dividends = Sub(_dividends, _indirectReferralBonus)
        # if _account has no indirect referral, 10% of _ongAmount will be the final _dividends
    #  add condition to avoid the first person who buys tokens to give 1% to team
    elif _oldFakeTotalSupply != 0:
        # This 1% will be treated as commission
        _commission_part = Div(_ongAmount, 100)
        _newCommissionAmount = Add(getCommissionAmount(), _commission_part)
        Put(GetContext(), COMMISSION_KEY, _newCommissionAmount)
        # Update the _dividends, the left 19% of _ongAmount will go to token holders
        _dividends = Sub(_dividends, _commission_part)
    # _dividends will be distributed to all the token holders, indicated through profitPerToken
    _profitPerToken = Get(GetContext(), PROFIT_PER_TOKEN_KEY)
    # if the buyer is not the first person to buy tokens
    if _oldFakeTotalSupply != 0:
        # multiply _dividends to make it dividable to _oldFakeTotalSupply, we will divide _profitPerToken when we actually use it
        _dividends = Mul(_dividends, largeNumber_)
        # the _account do not have the right to share the _dividends
        _profitPerToken = Add(Div(_dividends, _oldFakeTotalSupply), _profitPerToken)
        # Update the _profitPerToken
        Put(GetContext(), PROFIT_PER_TOKEN_KEY, _profitPerToken)
    else:
        if _dividends != 0:
            Put(GetContext(), COMMISSION_KEY, Add(getCommissionAmount(), _dividends))
    # put present dividend into dividend vault, update profit per token and dividend vault
    _collectDividendOf(_account)

    # record the _profitPerToken value after the _account buys in for _account to count his share till _profitPerToken later
    Put(GetContext(), _concatKey(_account, PROFIT_PER_TOKEN_FROM_SUFFIX), _profitPerToken)

    # Update the token balance of _account
    Put(GetContext(), _concatKey(_account, TOKEN_BALANCE_SUFFIX), Add(getBalanceOf(_account), _purchaseTokenAmount))
    # Update the totalSupply of token
    Put(GetContext(), TOTAL_SUPPLY_KEY, _newTotalTokenSupply)
    # Update the fakeTotalSupply of token
    Put(GetContext(), FAKE_TOTAL_SUPPLY_FOR_HOLDER_DIVIDENDS_KEY, _newFakeTotalSupply)

    # Update total ONG balance of this contract
    _newtotalOngAmount = Add(totalOngAmount(), _ongAmount)
    Put(GetContext(), TOTAL_ONG_KEY, _newtotalOngAmount)

    # Update ONG balance of this contract for key
    _newtotalOngAmountForKey = Add(totalOngAmountForKey(), _pureOngAmount)
    Put(GetContext(), TOTAL_ONG_FOR_TOKEN_KEY, _newtotalOngAmountForKey)

    # Broadcast the event
    _onTokenPurchase(_account, _ongAmount, _purchaseTokenAmount, _directReferral)

    return True

def _collectDividendOf(account):
    """
    put present dividend into dividend vault, update profit per token and dividend vault
    :param account:
    :return: True means it has been successfully run
    """
    _unsharedProfitPerTokenAfter = profitPerTokenFromOf(account)
    _profitPerTokenNow = Get(GetContext(), PROFIT_PER_TOKEN_KEY)
    # if addr is a manager, he will share 50% more of holder dividends
    _unsharedProfitIntervalPerToken = Sub(_profitPerTokenNow, _unsharedProfitPerTokenAfter)

    if _unsharedProfitIntervalPerToken != 0:
        Put(GetContext(), _concatKey(account, DIVIDEND_VAULT_SUFFIX), getDividendBalanceOf(account))
        Put(GetContext(), _concatKey(account, PROFIT_PER_TOKEN_FROM_SUFFIX), _profitPerTokenNow)

    return True

def _antiEarlyWhale(_account, _ongAmount):
    """

    :param _account:
    :param _ongAmount:
    :return:
    """
    RequireWitness(_account)
    _AntiEarlyWhale = Get(GetContext(), ANTI_EARLY_WHALE_KEY)
    # Still in the early stage
    if _AntiEarlyWhale == _POSITIVE_:
        # total ONG is less than 10000
        if totalOngAmount()  <= AntiEarlyWhaleQuota_:
            # if _account is admin, can also use [if checkAdmin(_account):]
            # if Get(GetContext(), _concatKey(_account, ADMIN_SUFFIX)) == _POSITIVE_:
            if checkAdmin(_account) == True:
                # How many token admin holds
                _adminTokenBalance = Get(GetContext(), _concatKey(_account, TOKEN_BALANCE_SUFFIX))
                # How many ong do these tokens equal
                _adminBoughtOng = _calculateSellTokenToOng(_adminTokenBalance)
                if Add(_adminBoughtOng, _ongAmount) <= adminQuota_:
                    return True
                else:
                    Notify(["Idiot admin, you cannot buy too many tokens"])
                    return False
            #  _account is manager
            # elif Get(GetContext(), _concatKey(_account, MANAGER_SUFFIX)) == _POSITIVE_:
            elif checkManager(_account) == True:
                # How many token the manager holds
                _managerTokenBalance = Get(GetContext(), _concatKey(_account, TOKEN_BALANCE_SUFFIX))
                # How many ong do these tokens equal
                _managerBoughtOng = _calculateSellTokenToOng(_managerTokenBalance)
                if Add(_managerBoughtOng, _ongAmount) <= managerQuota_:
                    return True
                else:
                    return False
            # _account is customer
            else:
                # How many token the customer holds
                _customerTokenBalance = Get(GetContext(), _concatKey(_account, TOKEN_BALANCE_SUFFIX))
                # How many ong do these tokens equal
                _customerBoughtOng = _calculateSellTokenToOng(_customerTokenBalance)
                if Add(_customerBoughtOng, _ongAmount) <= customerQuota_:
                    return True
                else:
                    Notify(["Man, you are too greedy", _account])
                    return False
        else:
            Put(GetContext(), ANTI_EARLY_WHALE_KEY, _NEGATIVE_)
            return True
    return True

def _calculateBuyOngToToken(_ongAmount):
    """
    Internal function to calculate token price based on an amount of incoming ong: M => Q
    a * Q^2 + b * Q + c = 0
    a = 1, b = 180000 * 10^5, c = -2 * 10^9 * 10^5 * M
    Delta = sqrt(b^2 - 4 * a * c)
    :param _ongAmount: say, 0.1 ONG should be 100000000
    :return: tokenAmount, say 1 token should be 10000
    """
    Q = totalSupply()
    M = totalOngAmountForKey()
    M1 = Add(M, _ongAmount)
    # _deltaQToDeltaP = 10^5
    _deltaQToDeltaP = Get(GetContext(), QUANTITY_INCREASE_PER_PRICE_KEY)
    # const = 90000
    const = Sub(initialTokenPrice(), initialTokenPriceIncremental())
    b = Mul(Mul(2, const), _deltaQToDeltaP)
    # minus_c is a positive value
    minus_c = Mul(Mul(Mul(2, tokenMagnitude_), _deltaQToDeltaP), M1)
    Delta = Sqrt(Add(Pwr(b, 2), Mul(4, minus_c)))
    Q1 = Div(Sub(Delta, b), 2)
    res = Sub(Q1, Q)
    return res

def _calculateSellTokenToOng( _tokenAmount):
    """
    internal function to calculate token sell price: Q => M
    M(Q) = [90000 + (Q * 10^(-5) + 90000)] / 2 * Q / 10^9
    :param _tokenAmount: amount of token, say, 1 token should be 10000
    :return: sell price, say, 0.1 ONG should be 100000000
    """
    Q = totalSupply()
    M = totalOngAmountForKey()
    Q1 = Sub(Q, _tokenAmount)
    # _deltaQToDeltaP = 10^5
    _deltaQToDeltaP = Get(GetContext(), QUANTITY_INCREASE_PER_PRICE_KEY)
    # const = 90000
    const = Sub(initialTokenPrice(), initialTokenPriceIncremental())
    M1 =  Div(Div(Mul(Add(Mul(2, const), Div(Q1, _deltaQToDeltaP)), Q1), tokenMagnitude_), 2)
    res = Sub(M, M1)
    return res

def _transferONG(fromAcct, toAcct, amount):
    """
     transfer amount of ONG from fromAcct to toAcct
     :param fromAcct:
     :param toAcct:
     :param amount:
     :return:
     """
    if CheckWitness(fromAcct):
        param = state(fromAcct, toAcct, amount)
        res = Invoke(0, ONGContractAddress_, 'transfer', [param])
        if res and res == b'\x01':
            return True
        else:
            return False
    else:
        return False

def _transferONGFromContact(toAcct, amount):
    param = state(selfContractAddr_, toAcct, amount)
    res = Invoke(0, ONGContractAddress_, 'transfer', [param])
    if res and res == b'\x01':
        return True
    else:
        return False

def _concatKey(str1,str2):
    return concat(concat(str1, '_'), str2)
# ==================== Methods for Utility purpose Ends  =======================

# ======================= Start of defining and emitting event  ===========================
def _onTokenPurchase(_addr, _ongAmount, _tokenAmount, _referredBy):
    params = ["onTokenPurchase", _addr, _ongAmount, _tokenAmount, _referredBy]
    Notify(params)
    return True

def _onWithdraw(_addr, _dividends):
    params = ["onWithdraw", _addr, _dividends]
    Notify(params)
    return True
def _onTransferOng(_from, _to, _amount):
    params = ["onTransferOng", _from, _to, _amount]
    Notify(params)
    return True

def _onTokenSell(_addr, _tokenAmount, _taxedOng):
    params = ["onTokenSell", _addr, _tokenAmount, _taxedOng]
    Notify(params)
    return True

def _onReinvest(_addr, _dividends, _tokenAmount):
    params = ["onReinvest", _addr, _dividends, _tokenAmount]
    Notify(params)
    return True
# ======================= End of defining and emitting event  ===========================


"""
SafeCheck.py
"""
def Require(condition):
	"""
	If condition is not satisfied, return false
	:param condition: required condition
	:return: True or false
	"""
	if not condition:
		Revert()
	return True

def RequireScriptHash(key):
    """
    Checks the bytearray parameter is script hash or not. Script Hash
    length should be equal to 20.
    :param key: bytearray parameter to check script hash format.
    :return: True if script hash or revert the transaction.
    """
    Require(len(key) == 20)
    return True

def RequireWitness(witness):
    """
	Checks the transaction sender is equal to the witness. If not
	satisfying, revert the transaction.
	:param witness: required transaction sender
	:return: True if transaction sender or revert the transaction.
	"""
    Require(CheckWitness(witness))
    return True

"""
SafeMath.py
"""

def Add(a, b):
    """
	Adds two numbers, throws on overflow.
	"""
    c = a + b
    Require(c >= a)
    return c

def Sub(a, b):
    """
	Substracts two numbers, throws on overflow (i.e. if subtrahend is greater than minuend).
    :param a: operand a
    :param b: operand b
    :return: a - b if a - b > 0 or revert the transaction.
	"""
    Require(a>=b)
    return a-b

def Mul(a, b):
    """
	Multiplies two numbers, throws on overflow.
    :param a: operand a
    :param b: operand b
    :return: a - b if a - b > 0 or revert the transaction.
	"""
    if a == 0:
        return 0
    c = a * b
    Require(c / a == b)
    return c

def Div(a, b):
    """
	Integer division of two numbers, truncating the quotient.
	"""
    Require(b > 0)
    c = a / b
    return c

def Pwr(a, b):
    """
    a to the power of b
    :param a the base
    :param b the power value
    :return a^b
    """
    c = 0
    if a == 0:
        c = 0
    elif b == 0:
        c = 1
    else:
        i = 0
        c = 1
        while i < b:
            c = Mul(c, a)
            i = i + 1
    return c

def Sqrt(a):
    """
    Return sqrt of a
    :param a:
    :return: sqrt(a)
    """
    c = Div(Add(a, 1), 2)
    b = a
    while(c < b):
        b = c
        c = Div(Add(Div(a, c), c), 2)
    return c
"""
Utils.py
"""

def Revert():
    """
    Revert the transaction. The opcodes of this function is `09f7f6f5f4f3f2f1f000f0`,
    but it will be changed to `ffffffffffffffffffffff` since opcode THROW doesn't
    work, so, revert by calling unused opcode.
    """
    raise Exception(0xF1F1F2F2F3F3F4F4)
