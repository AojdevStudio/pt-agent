"""CLI commands for managing research documents and searching the knowledge base."""

from typing import Optional
import typer
import os
from personal_ai_trainer.agents.research_agent.agent import ResearchAgent
from personal_ai_trainer.di.provider import get_supabase_client
from personal_ai_trainer.knowledge_base import repository as kb_repo

app = typer.Typer(help="Commands for managing research documents and searching the knowledge base.")

@app.command("add")
def add_document(title: str = typer.Option(..., prompt=True, help="Title of the research document."),
                 file_path: str = typer.Option(..., prompt=True, help="Path to the research document file."),
                 tags: Optional[str] = typer.Option(None, help="Comma-separated tags for the document.")):
    """
    Add a research document to the knowledge base.
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            typer.echo(f"Error: File not found at {file_path}")
            raise typer.Exit(code=1)

        # For PDF files, we'll just use the file path and extract text later
        # For simplicity, we'll use a placeholder text for now
        content = f"Content from {file_path} - This is a placeholder for PDF content."

        # Create research agent
        research_agent = ResearchAgent(supabase_client=get_supabase_client())

        # Process document
        summary = research_agent.process_research_document(
            content=content,
            source=os.path.basename(file_path),
            title=title
        )

        typer.echo(f"Added research document: {title} (File: {file_path}, Tags: {tags if tags else 'None'})")
        typer.echo(f"Summary: {summary}")
    except Exception as e:
        typer.echo(f"Error adding document: {str(e)}")
        raise typer.Exit(code=1)


@app.command("list")
def list_documents():
    """
    View available research documents.
    """
    try:
        # Get Supabase client
        client = get_supabase_client()

        # Query the kb_chunks table
        response = client.table(kb_repo.TABLE_NAME).select('doc_id, chunk_id, content, created_at').execute()

        if response.data:
            typer.echo("Available research documents:")
            for doc in response.data:
                # Show a preview of the content (first 50 characters)
                content_preview = doc['content'][:50] + "..." if len(doc['content']) > 50 else doc['content']
                typer.echo(f"- Document ID: {doc['doc_id']}, Chunk: {doc['chunk_id']}")
                typer.echo(f"  Preview: {content_preview}")
                typer.echo(f"  Added: {doc['created_at']}")
                typer.echo("")
        else:
            typer.echo("No documents found in the knowledge base.")
    except Exception as e:
        typer.echo(f"Error listing documents: {str(e)}")
        raise typer.Exit(code=1)


@app.command("search")
def search_documents(query: str = typer.Argument(..., help="Search query for the knowledge base.")):
    """
    Search the knowledge base for research documents.
    """
    try:
        # Create research agent
        research_agent = ResearchAgent(supabase_client=get_supabase_client())

        # Query the knowledge base
        answer = research_agent.query_knowledge_base(query)

        typer.echo(f"Search results for '{query}':")
        typer.echo(answer)
    except Exception as e:
        typer.echo(f"Error searching documents: {str(e)}")
        raise typer.Exit(code=1)