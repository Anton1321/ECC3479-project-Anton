# Rental Market Turnover and Rent Growth in Melbourne Suburbs, 2018-2025

**Anton Kozlovsky** (Student ID 36194239)
ECC3479 Data and Evidence in Economics, Monash University, May 2026
Repository: https://github.com/Anton1321/ECC3479-project-Anton

## 1. Introduction

Melbourne's rental market has been one of the most-discussed sectors of the Australian economy over the 2018-2025 sample window. Rents fell during the city's extended COVID-19 lockdowns, then rebounded sharply from 2022 onwards as international demand returned and supply remained tight. Understanding what predicts suburb-level rent growth is a question of both academic and policy interest.

The original research design asked: *what is the effect of a suburb's rental vacancy rate on subsequent rent growth in Melbourne?* The standard explanatory variable, suburb-level vacancy rates from SQM Research, was unobtainable for this submission: SQM's commercial price is ~$5,000 AUD, Monash University does not subscribe to CoreLogic / RP Data / Cotality, and academic-access requests did not return data in time. As a substitute we use the **moving annual count of new bond lodgements per suburb**, extracted from the same DFFH spreadsheet that supplies the rent figures. A new bond marks a new tenancy; the count by suburb-quarter is the closest free, suburb-level, quarterly measure of rental market activity available. It is a proxy for *turnover*, not vacancy. We are explicit throughout about what that substitution costs.

The refined question is therefore: *does within-suburb variation in lagged rental market turnover predict subsequent rent growth in Melbourne, controlling for common time shocks and the lagged rent level?* **Declared ambition: descriptive.** The estimates below identify a conditional within-suburb correlation, not a causal effect.

**What we find.** In a two-way fixed-effects panel of 110 Melbourne suburbs across 30 quarters (3,300 suburb-quarter observations), a 1% higher lagged log bond count is associated with about 0.019 percentage points lower next-quarter rent growth, controlling for the lagged log rent level (Table 2, column 4; coefficient -1.875, cluster-robust SE 0.439, t = -4.27). The headline survives changing the standard error estimator, trimming outliers, dropping the COVID era, and replication on the pre-2018 era of the same panel (where the same sign appears at a smaller magnitude of -0.630). The only variation that overturns it is dropping the rent-level control, which flips the sign - a textbook case of omitted variable bias explained in Section 4. The report follows the suggested structure, merging discussion, limitations and conclusion into Section 6.

## 2. Data

**Source.** Victorian Department of Families, Fairness and Housing, *Rental Report - Quarterly: Moving Annual Rents by Suburb* (data.vic.gov.au, CC-BY 4.0). Each suburb-quarter cell contains a moving annual median weekly rent and a moving annual count of new bond lodgements, both derived from the universe of formal residential tenancies in Victoria.

**Sample construction.** `code/01_clean_data.py` keeps the nine DFFH Melbourne metropolitan sub-regions, drops Group Total subtotals, reshapes the wide quarterly columns into long format, and filters to 2018 Q1 onwards. The result is a balanced panel of 110 suburbs across 31 quarters (3,410 obs). The analysis sample drops the first quarter of each suburb (no usable lag), yielding **3,300 obs across 110 suburbs and 30 quarters**.

**Derived variables.** `rent_growth` (quarter-on-quarter % change in median rent), one-quarter lags of rent and bond count within each suburb, and the logs `log_bond_count = ln(bond_count + 1)` and `log_lag_median_rent = ln(lag_median_rent)`. Bond counts span two orders of magnitude across suburbs (range 38 to 17,354) so the log transformation normalises the distribution and gives a semi-elasticity interpretation in the regression.

**The proxy.** Vacancy measures the *stock* of empty properties; bond lodgements measure the *flow* of new tenancies. The two are related but not identical (a market can have low vacancy and low turnover, or high vacancy and high turnover). The proxy is therefore an upper bound on what we can infer about vacancy itself; we describe the relationship between rental market *activity* and rent growth, not the textbook vacancy-rents relationship.

**Table 1: Summary statistics, analysis sample (2018 Q1 - 2025 Q3, n = 3,300)**

| Variable | Mean | SD | Min | Median | Max |
|---|---|---|---|---|---|
| Quarterly rent growth (%) | 1.16 | 2.33 | -11.11 | 0.84 | 14.58 |
| log(lag bond count) | 7.22 | 0.67 | 3.66 | 7.23 | 9.76 |
| log(lag median rent) | 6.16 | 0.18 | 5.77 | 6.13 | 6.77 |
| Median rent (AUD/week) | 484.91 | 90.26 | 330.00 | 470.00 | 868.00 |
| Bond count (moving annual) | 1,709.38 | 1,542.51 | 38.00 | 1,369.50 | 17,354.00 |

*Source: `code/03_analysis.ipynb` Section 1. Each row is one suburb-quarter observation.*

## 3. Empirical Strategy

The preferred regression is a two-way fixed-effects model with one control:

> *rent_growth*<sub>it</sub> = β · *lag_log_bond_count*<sub>it</sub> + δ · *log(lag_median_rent)*<sub>it</sub> + α<sub>i</sub> + γ<sub>t</sub> + ε<sub>it</sub>

α<sub>i</sub> (suburb FE) absorbs every time-invariant suburb characteristic - region, baseline rent level, dwelling composition, distance to the CBD. γ<sub>t</sub> (quarter FE) absorbs every Melbourne-wide shock - COVID lockdowns, RBA cash rate, federal housing policy. The control δ removes the systematic relationship between rent level and rent growth (mean reversion). With both fixed effects, β is identified entirely from *within-suburb, within-quarter* variation: when a particular suburb has unusually high turnover relative to both its own average and the Melbourne-wide quarter average, does its rent grow unusually slowly? Standard errors are cluster-robust at the suburb level (110 clusters, well above the Angrist-Pischke threshold of 42). The regressor is lagged to mitigate simultaneity with contemporaneous shocks. Bond count and rent are both logged because both are right-skewed.

**Declared ambition: descriptive.** The estimates identify a conditional within-suburb correlation. They are not a causal effect of turnover (let alone vacancy) on rents. Reverse causality (rents push tenants to move, generating new bonds) and the turnover-vs-vacancy proxy gap remain in the residual; both are discussed in Section 6.

## 4. Results

**Main results.** Table 2 reports four nested specifications, building from the simplest pooled OLS to the preferred two-way fixed-effects model with the rent control. The coefficient of interest is β, the loading on the lagged log bond count.

**Table 2: Main results - bond turnover and rent growth in Melbourne suburbs**
*Dependent variable: quarter-on-quarter rent growth (%); standard errors in parentheses*

<table>
<tr><th width="28%"></th><th width="18%">(1) Pooled OLS</th><th width="18%">(2) +Suburb FE</th><th width="18%">(3) TWFE</th><th width="18%">(4) TWFE + log(rent)</th></tr>
<tr><td width="28%">log(lag bond count)</td><td width="18%">-0.050</td><td width="18%">-0.790**</td><td width="18%">+0.291</td><td width="18%"><b>-1.875***</b></td></tr>
<tr><td width="28%"></td><td width="18%">(0.081)</td><td width="18%">(0.359)</td><td width="18%">(0.341)</td><td width="18%"><b>(0.439)</b></td></tr>
<tr><td width="28%">log(lag median rent)</td><td width="18%"></td><td width="18%"></td><td width="18%"></td><td width="18%">-11.998***</td></tr>
<tr><td width="28%"></td><td width="18%"></td><td width="18%"></td><td width="18%"></td><td width="18%">(0.790)</td></tr>
<tr><td width="28%">Suburb FE</td><td width="18%">No</td><td width="18%">Yes</td><td width="18%">Yes</td><td width="18%">Yes</td></tr>
<tr><td width="28%">Quarter FE</td><td width="18%">No</td><td width="18%">No</td><td width="18%">Yes</td><td width="18%">Yes</td></tr>
<tr><td width="28%">SE type</td><td width="18%">HC3</td><td width="18%">Cluster (suburb)</td><td width="18%">Cluster (suburb)</td><td width="18%">Cluster (suburb)</td></tr>
<tr><td width="28%">N (suburb-quarters)</td><td width="18%">3,300</td><td width="18%">3,300</td><td width="18%">3,300</td><td width="18%">3,300</td></tr>
<tr><td width="28%">N suburbs</td><td width="18%">110</td><td width="18%">110</td><td width="18%">110</td><td width="18%">110</td></tr>
</table>

*\* p<0.10, ** p<0.05, \*** p<0.01. Source: `code/03_analysis.ipynb` Section 3.*

**Reading the table.** Pooled OLS (col 1) returns essentially zero. Suburb FE (col 2) turns the within-suburb correlation negative and significant. Adding quarter FE (col 3) brings it back to near-zero - common time variation was driving column 2. The preferred col 4 adds the lagged log rent control: the turnover coefficient sharpens to -1.875 (t = -4.27) and rent level enters at -12.0 (t = -15.2), confirming strong mean reversion.

**Interpretation.** A 1% higher lagged bond-lodgement count in a Melbourne suburb is associated with about 0.019 percentage points lower next-quarter rent growth, holding constant every time-invariant suburb feature, every common Melbourne-wide time shock, and the lagged rent level. A doubling of turnover corresponds to about 1.3 percentage points lower rent growth - substantial relative to the sample mean of 1.16% per quarter, and close to two-thirds of one standard deviation of the dependent variable.

**Why the rent control matters.** Col 4 differs from col 3 only by adding log(lag rent), but the turnover coefficient swings by more than two points. This is the OVB formula made visible: turnover and rent levels are positively correlated within suburbs (denser areas have both more turnover and higher rents), while rent levels strongly and negatively predict rent growth (mean reversion). The product is a positive bias of about +2 percentage points in col 3, which masks the underlying negative within-suburb relationship that col 4 recovers.

**Two extensions, briefly.** *Regional heterogeneity* (Section 5 of `code/03_analysis.ipynb`): the relationship is concentrated in middle and outer suburbs (β = -2.15, 88 suburbs) and absent in Inner Melbourne (β = +0.96, 22 suburbs, not significant), consistent with bond counts being a noisier slack signal in dense inner-city apartment markets. *DiD around COVID* (Section 4 of the same notebook): interacting turnover with a post-2020 Q2 indicator yields a pre-COVID coefficient of -2.14 and an interaction of +0.16 (not significant), so the within-suburb relationship is stable across the COVID structural break.

![Figure 1](../outputs/coefficient_plot.png)

*Figure 1: Turnover coefficient (with 95% confidence intervals) across the four main specifications in Table 2. The estimate is essentially zero in pooled OLS (1), drifts negative with suburb FE (2), returns to near-zero once quarter FE absorbs common shocks (3), and becomes precisely negative only when log(lag median rent) is added as a control (4). Source: `code/03_analysis.ipynb` Section 3.*

## 5. Robustness

The main result was stress-tested through six defensible variations probing distinct assumptions (Lecture 9). Table 4 reports all seven columns side by side.

**Table 4: Robustness of the turnover coefficient**
*Dependent variable: quarter-on-quarter rent growth (%); standard errors in parentheses*

<table>
<tr><th width="18%"></th><th width="11%">(C1) Main</th><th width="12%">(C2) HC3 only</th><th width="11%">(C3) Cluster=region</th><th width="11%">(C4) No rent ctrl</th><th width="12%">(C5) Trim 1%/99%</th><th width="12%">(C6) Drop COVID</th><th width="13%">(C7) Placebo pre-2018</th></tr>
<tr><td width="18%">log(lag bond count)</td><td width="11%"><b>-1.875***</b></td><td width="12%">-1.875***</td><td width="11%">-1.875***</td><td width="11%">+0.291</td><td width="12%">-1.891***</td><td width="12%">-1.688***</td><td width="13%">-0.630***</td></tr>
<tr><td width="18%"></td><td width="11%"><b>(0.439)</b></td><td width="12%">(0.351)</td><td width="11%">(0.541)</td><td width="11%">(0.345)</td><td width="12%">(0.397)</td><td width="12%">(0.449)</td><td width="13%">(0.144)</td></tr>
<tr><td width="18%">log(lag median rent)</td><td width="11%">-11.998***</td><td width="12%">-11.998***</td><td width="11%">-11.998***</td><td width="11%">-</td><td width="12%">-10.414***</td><td width="12%">-14.959***</td><td width="13%">-8.036***</td></tr>
<tr><td width="18%"></td><td width="11%">(0.790)</td><td width="12%">(1.094)</td><td width="11%">(1.008)</td><td width="11%">-</td><td width="12%">(0.767)</td><td width="12%">(1.379)</td><td width="13%">(0.725)</td></tr>
<tr><td width="18%">Suburb FE / Quarter FE</td><td width="11%">Yes / Yes</td><td width="12%">Yes / Yes</td><td width="11%">Yes / Yes</td><td width="11%">Yes / Yes</td><td width="12%">Yes / Yes</td><td width="12%">Yes / Yes</td><td width="13%">Yes / Yes</td></tr>
<tr><td width="18%">Sample</td><td width="11%">2018-2025</td><td width="12%">2018-2025</td><td width="11%">2018-2025</td><td width="11%">2018-2025</td><td width="12%">2018-2025 trim</td><td width="12%">2018-2025 ex-COVID</td><td width="13%">2000-2017</td></tr>
<tr><td width="18%">N (suburb-quarters)</td><td width="11%">3,300</td><td width="12%">3,300</td><td width="11%">3,300</td><td width="11%">3,300</td><td width="12%">3,234</td><td width="12%">2,530</td><td width="13%">7,802</td></tr>
</table>

*\* p<0.10, ** p<0.05, \*** p<0.01. Source: `code/04_robustness.ipynb` Section 5. (C2)-(C3) vary the SE estimator. (C4) drops the rent control. (C5) trims the top and bottom 1% of rent growth. (C6) drops 2020 Q2 - 2021 Q4 (COVID era). (C7) is a wrong-period placebo on the pre-2018 era of the same DFFH panel.*

**What survives and what does not.** *Inference (C2, C3):* point estimate is unchanged across HC3 and cluster-by-region; t-statistic stays above 3 in all three columns. *Controls (C4):* dropping log(lag rent) flips the sign to +0.29, the OVB pattern from Section 4 made visible - reported as a structural failure because that is what it is. *Sample (C5, C6):* trimming the top and bottom 1% of growth removes 66 observations and barely moves the coefficient; dropping the COVID era removes 770 observations and shrinks the coefficient only 10% (-1.69) - the post-COVID rebound is not driving the headline. *Placebo (C7):* the same specification on the pre-2018 era (7,802 obs) returns -0.630, same sign and 1% significant, but a third of the magnitude. The relationship is stable across 25 years; its intensity in the post-2018 window may be partly era-specific.

**Summary: 6 of 7 checks support the headline; the 1 failure (C4) is structural and explainable.**

![Figure 2](../outputs/robustness_coefficient_plot.png)

*Figure 2: Turnover coefficient (with 95% confidence intervals) across the seven robustness specifications in Table 4. The main estimate (C1) is in blue; the OVB-revealing failure (C4) in orange; the pre-2018 placebo (C7) in green. Source: `code/04_robustness.ipynb` Section 6.*

## 6. Discussion, Limitations, and Conclusion

**What we can conclude.** Within Melbourne's 110 suburbs over 2018-2025, there is a statistically reliable, economically meaningful, and largely robust within-suburb conditional correlation between lagged bond-lodgement turnover and subsequent rent growth. The relationship is negative, survives every defensible analytical variation except the one that mechanically introduces omitted variable bias, and is visible in the pre-2018 era of the same panel.

**Four limits, in increasing order of importance:** (i) Fixed effects strip all between-suburb variation, so the analysis cannot rank suburbs or comment on which areas are tightest. (ii) Melbourne is one city with its own institutions - generalisation is not warranted. (iii) Reverse causality from rents to turnover is real; we lag the regressor as a partial fix, not a full one. (iv) **The proxy gap.** Bond turnover is not a vacancy rate. A high-turnover quarter could reflect either excess supply being absorbed (rents soften) or strong demand churning through existing units (rents do not). The fixed-effects design cannot decompose the mechanism. A negative coefficient is consistent with the first story but does not rule out the second. This is the structural reason the analysis is declared descriptive.

**What would resolve the remaining threat.** Suburb-level vacancy rates from SQM Research, Cotality, or PropTrack - ideally via Monash Library or the RoZetta Institute academic-access partnership. With proper vacancy data the same panel design re-estimates cleanly, with turnover relegated to a robustness check. Beyond that, a causal estimate would require an instrument for vacancy that shifts supply or accessibility independently of contemporaneous rents (rezoning timing, new public transport openings) - beyond this submission.

**Conclusion.** The free data we have supports a careful descriptive claim about Melbourne's rental dynamics: turnover and rent growth co-move within suburbs in a stable way that holds before, during, and after the COVID shock. Promoting that pattern to a structural statement about vacancy → rents requires data we could not obtain. The honest version is the version we report.

## References

Angrist, J.D. & Pischke, J.-S. (2009). *Mostly Harmless Econometrics: An Empiricist's Companion.* Princeton University Press.

Card, D. & Krueger, A.B. (1994). Minimum wages and employment: A case study of the fast-food industry in New Jersey and Pennsylvania. *American Economic Review* 84(4), 772-793.

Ellis, K. (2026). *ECC3479 Data and Evidence in Economics* (lectures 5-9). Monash University, March-May 2026.

Imbens, G.W. & Angrist, J.D. (1994). Identification and estimation of local average treatment effects. *Econometrica* 62(2), 467-475.

MacKinnon, J.G. & White, H. (1985). Some heteroskedasticity-consistent covariance matrix estimators with improved finite sample properties. *Journal of Econometrics* 29(3), 305-325.

Moulton, B.R. (1986). Random group effects and the precision of regression estimates. *Journal of Econometrics* 32(3), 385-397.

Victorian Department of Families, Fairness and Housing. *Rental Report - Quarterly: Moving Annual Rents by Suburb.* data.vic.gov.au, accessed for the September 2025 release. Creative Commons Attribution 4.0 International.

White, H. (1980). A heteroskedasticity-consistent covariance matrix estimator and a direct test for heteroskedasticity. *Econometrica* 48(4), 817-838.
