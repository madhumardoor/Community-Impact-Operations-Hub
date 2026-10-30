from mcp.server.fastmcp import FastMCP
from backend.db import get_connection
from backend.main import retrieve_sop_context
mcp = FastMCP('community-impact-operations-hub')

@mcp.tool()
def get_volunteer_summary() -> dict:
    """Return aggregate counts only; does not expose personal records."""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute('SELECT status,COUNT(*) AS count FROM volunteers GROUP BY status ORDER BY status')
        statuses=cur.fetchall()
        cur.execute('SELECT COUNT(*) AS count FROM volunteers')
        volunteers=cur.fetchone()['count']
        cur.execute('SELECT COUNT(*) AS count FROM assignments')
        assignments=cur.fetchone()['count']
    return {'total_volunteers':volunteers,'total_assignments':assignments,'by_status':statuses}

@mcp.tool()
def search_volunteer_sop(question: str) -> str:
    """Search sample SOP text for relevant context."""
    if not question or len(question)>1000:
        return 'Provide a question up to 1000 characters.'
    return retrieve_sop_context(question)

if __name__ == '__main__':
    mcp.run()
