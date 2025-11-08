def asp_state():
    return """
# ASP.NET State Management

ViewState["name"] = "Bipin";
Session["user"] = "Bipin";
Response.Cookies["city"].Value = "Mumbai";
"""
