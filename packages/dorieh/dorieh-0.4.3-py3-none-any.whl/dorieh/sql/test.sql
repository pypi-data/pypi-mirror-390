/*
 * Copyright (c) 2025. Harvard University
 *
 * Developed by Research Software Engineering,
 * Harvard University Research Computing and Data (RCD) Services.
 *
 * Author: Michael A Bouzinier
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *          http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 *
 *
 *
 *
 */

select
    public.count_rows('medicare', 'beneficiaries') As NumBeneficiaries,
    public.count_rows('medicare', 'enrollments') As CountEnrollments,
    public.get_year('medicare'::varchar, 'enrollments'::varchar) As EnrollmentYears,
    public.count_rows('medicare', 'admissions') As NumAdmissions,
    public.count_rows('medicare_audit', 'admissions') As InvalidAdmissions,
    public.get_year('medicare'::varchar, 'admissions'::varchar) As AdmissionsYears,
    public.get_year('medicare_audit'::varchar, 'admissions'::varchar) InvalidAdmissionYears;