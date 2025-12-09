"""Initial schema creation for Physical AI Book

Revision ID: 001
Revises:
Create Date: 2025-12-09 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create modules table
    op.create_table(
        'modules',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint('order >= 1 AND order <= 4'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order')
    )

    # Create chapters table
    op.create_table(
        'chapters',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('module_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('number', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=150), nullable=False),
        sa.Column('content_markdown', sa.Text(), nullable=False),
        sa.Column('learning_objectives', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('references', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('token_count', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), server_default='draft', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("number >= 1 AND number <= 12"),
        sa.CheckConstraint("status IN ('draft', 'published', 'archived')"),
        sa.ForeignKeyConstraint(['module_id'], ['modules.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('module_id', 'number', name='uq_chapter_module_number')
    )

    # Create content_chunks table
    op.create_table(
        'content_chunks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('chapter_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('section_title', sa.String(length=100), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('token_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['chapter_id'], ['chapters.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create rag_queries table
    op.create_table(
        'rag_queries',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('query_text', sa.String(length=500), nullable=False),
        sa.Column('retrieval_mode', sa.String(length=20), nullable=False),
        sa.Column('chapter_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('selected_text', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('response_status', sa.String(length=20), nullable=False),
        sa.CheckConstraint("retrieval_mode IN ('global', 'chapter-specific', 'text-selection')"),
        sa.CheckConstraint("response_status IN ('success', 'no_context', 'error')"),
        sa.ForeignKeyConstraint(['chapter_id'], ['chapters.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create retrieved_chunks table
    op.create_table(
        'retrieved_chunks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('query_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('chunk_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('similarity_score', sa.Numeric(precision=3, scale=2), nullable=False),
        sa.Column('rank', sa.Integer(), nullable=False),
        sa.CheckConstraint('similarity_score >= 0 AND similarity_score <= 1'),
        sa.CheckConstraint('rank >= 1 AND rank <= 5'),
        sa.ForeignKeyConstraint(['query_id'], ['rag_queries.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indices
    op.create_index('idx_chapters_module', 'chapters', ['module_id'])
    op.create_index('idx_chunks_chapter', 'content_chunks', ['chapter_id'])
    op.create_index('idx_queries_chapter', 'rag_queries', ['chapter_id'])
    op.create_index('idx_retrieved_query', 'retrieved_chunks', ['query_id'])


def downgrade() -> None:
    # Drop indices
    op.drop_index('idx_retrieved_query', 'retrieved_chunks')
    op.drop_index('idx_queries_chapter', 'rag_queries')
    op.drop_index('idx_chunks_chapter', 'content_chunks')
    op.drop_index('idx_chapters_module', 'chapters')

    # Drop tables
    op.drop_table('retrieved_chunks')
    op.drop_table('rag_queries')
    op.drop_table('content_chunks')
    op.drop_table('chapters')
    op.drop_table('modules')
