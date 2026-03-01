module.exports = async ({ github, context }) => {
  const marker = '<!-- testpypi-install-command -->';
  const body = [
    marker,
    '### TestPyPI package listo para probar',
    `- Package: \`${process.env.TESTPYPI_PACKAGE}\``,
    `- Version: \`${process.env.TESTPYPI_VERSION}\``,
    `- Install: \`${process.env.TESTPYPI_INSTALL_CMD}\``,
  ].join('\n');

  const issue_number = context.payload.pull_request.number;
  const { data: comments } = await github.rest.issues.listComments({
    owner: context.repo.owner,
    repo: context.repo.repo,
    issue_number,
    per_page: 100,
  });

  const existing = comments.find(
    (comment) =>
      comment.user?.type === 'Bot' &&
      comment.body &&
      comment.body.includes(marker)
  );

  if (existing) {
    await github.rest.issues.updateComment({
      owner: context.repo.owner,
      repo: context.repo.repo,
      comment_id: existing.id,
      body,
    });
  } else {
    await github.rest.issues.createComment({
      owner: context.repo.owner,
      repo: context.repo.repo,
      issue_number,
      body,
    });
  }
};