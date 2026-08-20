import { expect, test } from '@playwright/test';
import type { APIRequestContext } from '@playwright/test';

const CODIGO_BASE = `POP-E2E-${Date.now()}`;

async function seedPop(request: APIRequestContext, codigo: string, nome?: string) {
  const response = await request.post('/api/generate', {
    data: {
      nome_pop: nome ?? 'POP semeado via API',
      codigo,
      versao: '01',
      data: '17/08/2026',
      area: 'E2E',
      objetivo: 'Objetivo do POP de teste E2E.',
      escopo: '',
      aviso: '',
      definicoes: [],
      secoes: [],
      regras: [],
      consulta: '',
      revisoes: [],
    },
  });
  expect(response.ok(), await response.text()).toBeTruthy();
  return (await response.json()) as { pop_id: string };
}

test.describe.configure({ mode: 'serial' });

test('início mostra visão geral com KPIs reais e ações rápidas', async ({ page }) => {
  await page.goto('/');

  await expect(page.getByRole('heading', { name: 'Início' })).toBeVisible();

  const kpiSalvos = page.locator('.dash-kpi', { hasText: 'POPs salvos' });
  await expect(kpiSalvos.locator('.dash-kpi-value')).toHaveText('0');

  await expect(page.locator('.dash-section-title', { hasText: 'Ações rápidas' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Novo POP', exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Ir para a biblioteca' })).toBeVisible();

  await expect(page.locator('.dash-section-title', { hasText: 'Recentes (0)' })).toBeVisible();
  await expect(page.locator('.dash-empty')).toContainText('Nenhum POP salvo ainda.');
});

test('alterna tema claro/escuro', async ({ page }) => {
  await page.goto('/');
  const toggle = page.locator('.theme-toggle');
  const inicial = (await toggle.getAttribute('aria-pressed')) === 'true' ? 'dark' : 'light';
  const outro = inicial === 'dark' ? 'light' : 'dark';

  await toggle.click();
  await expect(page.locator('html')).toHaveAttribute('data-theme', outro);

  await toggle.click();
  await expect(page.locator('html')).toHaveAttribute('data-theme', inicial);
});

test('valida campos obrigatórios antes de gerar', async ({ page }) => {
  await page.goto('/formulario');
  await page.getByRole('button', { name: 'Gerar POP (.docx)', exact: true }).click();

  const alerta = page.locator('.alert-error');
  await expect(alerta).toContainText('Nome do POP é obrigatório.');
  await expect(alerta).toContainText('Código é obrigatório.');
  await expect(alerta).toContainText('Área é obrigatória.');
  await expect(alerta).toContainText('Objetivo é obrigatório.');
});

test('cria POP pelo formulário, gera e baixa .docx/.pdf', async ({ page }) => {
  const codigo = `${CODIGO_BASE}-01`;
  await page.goto('/');
  await page.getByRole('button', { name: 'Novo POP', exact: true }).click();

  await page.getByLabel('Nome do POP').fill('Planejamento da atracação E2E');
  await page.getByLabel('Código').fill(codigo);
  await page.getByLabel('Área').fill('Operações E2E');
  await page.getByLabel(/objetivo/i).first().fill('Planejamento da atracação de navio.');

  await page.getByRole('button', { name: 'Gerar POP (.docx)', exact: true }).click();
  await expect(page.locator('.alert-success')).toHaveText('POP gerado com sucesso.');

  const downloadDocx = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Baixar POP (.docx)' }).click();
  expect((await downloadDocx).suggestedFilename()).toMatch(new RegExp(`^${codigo}_.*\.docx$`));

  const downloadPdf = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Baixar POP (.pdf)' }).click();
  expect((await downloadPdf).suggestedFilename()).toMatch(/\.pdf$/);
});

test('histórico: carregar para editar e baixar backup .zip', async ({ page }) => {
  const { pop_id } = await seedPop(page.request, `${CODIGO_BASE}-HIST`);
  await page.goto('/formulario');

  const select = page.getByLabel('POP salvo');
  await expect(select).toBeVisible();
  await select.selectOption(pop_id);

  await page.getByRole('button', { name: 'Carregar para editar' }).click();
  await expect(page.getByLabel('Nome do POP')).toHaveValue('POP semeado via API');

  const downloadBackup = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Baixar backup (.zip)' }).click();
  expect((await downloadBackup).suggestedFilename()).toMatch(/^gerapop_backup_.*\.zip$/);
});

test('restaura rascunho persistido entre sessões', async ({ page }) => {
  await page.goto('/formulario');
  await page.waitForTimeout(600);
  await page.getByLabel('Nome do POP').fill('Rascunho persistente E2E');
  await page.getByLabel('Código').fill(`${CODIGO_BASE}-DRAFT`);
  await page.waitForTimeout(2500);
  await page.reload();

  await expect(page.getByLabel('Nome do POP')).toHaveValue('Rascunho persistente E2E');
  await expect(page.getByLabel('Código')).toHaveValue(`${CODIGO_BASE}-DRAFT`);
});

test('bloqueia código duplicado ao gerar', async ({ page }) => {
  const codigo = `${CODIGO_BASE}-DUP`;
  await seedPop(page.request, codigo);

  await page.goto('/formulario');
  await page.getByLabel('Nome do POP').fill('Segundo POP com mesmo código');
  await page.getByLabel('Código').fill(codigo);
  await page.getByLabel('Área').fill('E2E');
  await page.getByLabel(/objetivo/i).first().fill('Objetivo duplicado.');

  await page.getByRole('button', { name: 'Gerar POP (.docx)', exact: true }).click();
  await expect(page.locator('.alert-error')).toHaveText(
    new RegExp(`O código ${codigo} já é usado pelo POP`),
  );
});

test('exclui POP salvo com confirmação pela biblioteca', async ({ page }) => {
  const codigo = `${CODIGO_BASE}-DEL`;
  await seedPop(page.request, codigo, 'POP a ser excluído');
  const antigo = await page.request.get('/api/pops');
  const antes = ((await antigo.json()) as Array<{ id: string }>).length;

  await page.goto('/pops');
  const card = page.locator('.dash-card', { hasText: 'POP a ser excluído' }).first();
  await card.getByRole('button', { name: 'Excluir' }).click();

  const modal = page.locator('.modal');
  await expect(modal).toBeVisible();
  await modal.getByRole('button', { name: 'Sim, excluir' }).click();
  await expect(modal).toBeHidden();

  await expect(page.locator('.dash-card', { hasText: 'POP a ser excluído' })).toBeHidden();
  const novo = await page.request.get('/api/pops');
  expect(((await novo.json()) as Array<unknown>).length).toBe(antes - 1);
});