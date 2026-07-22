import apiClient from './index';
import { toCamelCase } from './utils';

export type MarketIndexSnapshot = {
  name: string;
  code: string;
  change: string;
  turnover: string;
  tone: 'up' | 'down' | 'flat';
};

export type MarketOverviewItem = {
  label: string;
  value: string;
  note: string;
};

export type EtfMarketOverviewResponse = {
  dataDate: string;
  source: string;
  marketIndices: MarketIndexSnapshot[];
  overview: MarketOverviewItem[];
  summary: string;
  errors: string[];
};

export const etfResearchApi = {
  async getMarketOverview(): Promise<EtfMarketOverviewResponse> {
    const response = await apiClient.get('/api/v1/etf-research/market-overview', {
      timeout: 60000,
    });
    return toCamelCase<EtfMarketOverviewResponse>(response.data);
  },
};
