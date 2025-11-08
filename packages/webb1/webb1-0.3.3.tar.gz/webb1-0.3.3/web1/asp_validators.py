def asp_validators():
    return """
# ASP.NET Validators

<asp:RequiredFieldValidator ControlToValidate="txtName" ErrorMessage="Required" />

<asp:CompareValidator ControlToValidate="txtAge" ValueToCompare="18" Operator="GreaterThan" Type="Integer" ErrorMessage="Must be 18+" />

<asp:RegularExpressionValidator ControlToValidate="txtEmail" ValidationExpression="\\S+@\\S+\\.\\S+" ErrorMessage="Invalid Email" />
"""
