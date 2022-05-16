*** Settings ***
Documentation       Playwright template.
Variables           MyConstants
Library             CheckCSVForValidInput     ${CSVURL}    ${TRUE}
Library             AuditSite    ${SITE}


*** Tasks ***
Main task
    Get Csv Hash Value
    Batch Submit Order
    
