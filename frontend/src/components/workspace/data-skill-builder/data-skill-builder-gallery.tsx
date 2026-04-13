"use client";

import { DatabaseIcon, PlusIcon } from "lucide-react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useI18n } from "@/core/i18n/hooks";

export function DataSkillBuilderGallery() {
  const { t } = useI18n();
  const router = useRouter();

  const handlePostgresSkill = () => {
    router.push("/workspace/data-skill-builder/build-skill");
  };

  return (
    <div className="flex size-full flex-col">
      <div className="flex items-center justify-between border-b px-6 py-4">
        <div>
          <h1 className="text-xl font-semibold">{t.dataSkillBuilder.title}</h1>
          <p className="text-muted-foreground mt-0.5 text-sm">
            {t.dataSkillBuilder.description}
          </p>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
          <Card className="cursor-pointer hover:border-primary transition-colors" onClick={handlePostgresSkill}>
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="bg-primary/10 flex h-12 w-12 items-center justify-center rounded-lg">
                  <DatabaseIcon className="text-primary h-6 w-6" />
                </div>
                <div>
                  <CardTitle>{t.dataSkillBuilder.postgresSkill}</CardTitle>
                  <CardDescription>
                    {t.dataSkillBuilder.postgresSkillDescription}
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <Button className="w-full">
                <PlusIcon className="mr-1.5 h-4 w-4" />
                {t.dataSkillBuilder.postgresSkill}
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
