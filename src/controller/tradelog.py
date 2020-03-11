""" Main tradelog controller """

# Controller rules:
# 1. return  Result class {'success': ?, 'message': ?, 'severity': ?}
# 2. pass db returns back to view to format
# 3. process here

from src.model.portfolio import Portfolio
from src.common.result import Result

def ports() -> list:
    """ Returns a list of portfolio names """
    return [port.name for port in Portfolio.all()]

def create_portfolio(port) -> Result:
    """ createa a new portfolio if the name doesn't already exist """
    if port['name'] in ports():
        return Result(success=False, message='This portfolio name already exists', 
                      severity='WARNING')
    return Portfolio(port).create()
