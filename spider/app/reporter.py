import datetime
import logging
from typing import List

import quantstats


class Reporter(object):
    logger = logging.getLogger(__name__)

    def report(self, results, strategy, log=False, csv=False) -> List:

        report_list = []

        if type(results) == strategy:
            # single run
            report_list.append(self._report_single(results, log=log))

        elif type(results) is list \
                and type(results[0]) == list \
                and type(results[0][0]) == strategy:
            # wfo
            report_list = report_list + self._report_multiple(results, log=log)

        elif type(results) is list:
            # optimization run
            report_list = report_list + self._report_multiple(results, log=log)

        else:
            self.logger.error("wtf")

        if csv:
            filename = "logs/report_" + str(int(datetime.datetime.now().timestamp())) + ".csv"

            with open(filename, "w") as fp:
                if len(report_list) > 0:
                    fp.write("Strategy\t" + str(strategy) + "\n")

                    headers = [k for k in report_list[0]]
                    headers.remove("params")
                    headers.insert(0, "params")

                    fp.write("\t".join(headers) + "\n")

                    for report in report_list:
                        fp.write("\t".join([str(report[h]) for h in headers]) + "\n")

        return report_list

    def _report_single(self, result, html=False, log=False):
        quantstats.extend_pandas()
        portfolio_stats = result.analyzers.getbyname('PyFolio')
        basic_stats = result.analyzers.getbyname('Basic_Stats')
        returns, positions, transactions, gross_lev = portfolio_stats.get_pf_items()
        returns.index = returns.index.tz_convert(None)

        if html:
            quantstats.reports.html(returns, output='logs/stats.html', title='CloseSMA')

        cagr = quantstats.stats.cagr(returns)
        sharpe = quantstats.stats.sharpe(returns)
        sortino = quantstats.stats.sortino(returns)
        volatility = quantstats.stats.volatility(returns)
        win = quantstats.stats.avg_win(returns)
        loss = quantstats.stats.avg_loss(returns)
        drawdown = quantstats.stats.max_drawdown(returns)

        if log:
            self.logger.info("---------------------------------")
            self.logger.info("Params: {}".format(result.params.__dict__))
            self.logger.info('CAGR: {:.3f}'.format(cagr))
            self.logger.info('Sharpe: {:.3f}'.format(sharpe))
            self.logger.info('Sortino: {:.3f}'.format(sortino))
            self.logger.info('Volatility: {:.3f}'.format(volatility))
            self.logger.info('Avg Win: {:.5f}'.format(win))
            self.logger.info('Avg Loss: {:.5f}'.format(loss))
            self.logger.info('Max Drawdown: {:.5f}'.format(drawdown))

        dict1 = self._print_trade_analysis(basic_stats.get_analysis(), log=log)

        dict2 = {
            'params': result.params.__dict__,
            'cagr': cagr,
            'sharpe': sharpe,
            'sortino': sortino,
            'volatility': volatility,
            'avg_win': win,
            'avg_loss': loss,
            'max_drawdown': drawdown,
        }

        return {**dict1, **dict2}

    def _report_multiple(self, results, log=False):
        a = []
        for r in results:
            for s in r:
                try:
                    a.append(self._report_single(s, log=log))
                except Exception:
                    self.logger.error("Error with parameters.")

        return a

    def _print_trade_analysis(self, analyzer, log=False):
        total_open = analyzer.total.open
        total_closed = analyzer.total.closed
        total_won = analyzer.won.total
        total_lost = analyzer.lost.total
        win_streak = analyzer.streak.won.longest
        lose_streak = analyzer.streak.lost.longest
        pnl_net = round(analyzer.pnl.net.total, 2)
        strike_rate = (total_won / total_closed) * 100

        h1 = ['Total Open', 'Total Closed', 'Total Won', 'Total Lost']
        h2 = ['Strike Rate', 'Win Streak', 'Losing Streak', 'PnL Net']
        r1 = [total_open, total_closed, total_won, total_lost]
        r2 = [strike_rate, win_streak, lose_streak, pnl_net]

        if len(h1) > len(h2):
            header_length = len(h1)
        else:
            header_length = len(h2)

        print_list = [h1, r1, h2, r2]
        row_format = "{:<15}" * (header_length + 1)

        if log:
            self.logger.info("Trade Analysis Results:")

            for row in print_list:
                self.logger.info(row_format.format('', *row))

        return {
            'total_open': total_open,
            'total_closed': total_closed,
            'total_won': total_won,
            'total_lost': total_lost,
            'win_streak': win_streak,
            'lose_streak': lose_streak,
            'pnl_net': pnl_net,
            'strike_rate': strike_rate,
        }
